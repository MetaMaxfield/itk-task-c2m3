import os
import time

import redis
import requests
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from requests.exceptions import RequestException
from rest_framework.status import HTTP_200_OK

from src.events.models import Event, Location
from src.events.serializers import EventSyncSerializer, LocationSyncSerializer
from src.sync.models import SyncResult

load_dotenv()


class Command(BaseCommand):
    help = "Synchronization of events"
    redis_host = "redis"
    redis_port = 6379
    redis_db = 1
    url = "https://events.k3scluster.tech/api/events/"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

        self.r = redis.Redis(
            self.redis_host, self.redis_port, self.redis_db, decode_responses=True
        )

        self.added_count = 0
        self.updated_count = 0

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=False)

        group.add_argument("--all", action="store_true", default=False)
        group.add_argument("--date", type=str, default=None)

    def update_quantity_counters(self, new_count, upd_count):
        self.added_count += new_count
        self.updated_count += upd_count

    def sync_locations(self, data):
        serializer = LocationSyncSerializer(
            data=data, many=True, context={"redis": self.r}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def sync_events(self, data):
        serializer = EventSyncSerializer(
            data=data, many=True, context={"redis": self.r}
        )
        serializer.is_valid(raise_exception=True)
        new_count, upd_count = serializer.save()

        self.update_quantity_counters(new_count, upd_count)

    def create_requests(self, url):
        retries = 5
        while url:
            try:
                response = requests.get(
                    url,
                    timeout=10,
                    headers={
                        "Authorization": f"Bearer {os.getenv('JWT_TOKEN')}",
                        "Content-Type": "application/json",
                    },
                )

            except RequestException:
                response = None

            if not response or response.status_code != HTTP_200_OK:
                self.stdout.write(
                    self.style.WARNING(
                        (
                            f"Unable to retrieve data for {url}. "
                            f"Remaining attempts: {retries}."
                        )
                    )
                )

                retries -= 1
                if retries == 0:
                    self.stdout.write(
                        self.style.ERROR(
                            (
                                "Synchronization was not completed because the service "
                                f"{url} was unavailable. The next synchronization "
                                "should be performed for all events in the database "
                                "(use '--all' flag)."
                            )
                        )
                    )
                    break
                time.sleep(5)
            else:
                self.stdout.write(f"Successful synchronization at {url}")

                data = response.json()

                locations_data = []
                for event_d in data["results"]:
                    if event_d["place"]:
                        locations_data.append(event_d["place"])
                        event_d["place_id"] = event_d["place"]["id"]

                self.sync_locations(locations_data)
                self.sync_events(data["results"])

                retries = 5

                url = data["next"]

    def handle(self, *args, **options):
        try:
            if self.r.scard("exists_location_ids") == 0:
                for uuid in Location.objects.values_list("id", flat=True):
                    self.r.sadd("exists_location_ids", str(uuid))
            if self.r.scard("exists_event_ids") == 0:
                for uuid in Event.objects.values_list("id", flat=True):
                    self.r.sadd("exists_event_ids", str(uuid))

            if self.r.scard("exists_event_ids") == 0:
                self.stdout.write(
                    self.style.NOTICE("First sync: getting all events...")
                )
                self.create_requests(self.url)

            elif options["all"] is True:
                self.stdout.write("Full synchronization of all events...")
                changed_at = self.r.get("min_changed_at") or str(
                    Event.objects.order_by("changed_at")
                    .first()
                    .changed_at.strftime("%Y-%m-%d")
                )
                self.create_requests(self.url + f"?changed_at={changed_at}")

            else:
                if options["date"] is None:
                    date = self.r.get("max_changed_at") or str(
                        Event.objects.order_by("-changed_at")
                        .first()
                        .changed_at.strftime("%Y-%m-%d")
                    )
                    self.stdout.write(
                        f"Sync all changes since the last successful sync {date}..."
                    )
                else:
                    date = options["date"]
                    self.stdout.write(f"Sync all changes since date {date}...")

                self.create_requests(self.url + f"?changed_at={date}")

            self.r.set(
                "min_changed_at",
                str(
                    Event.objects.order_by("changed_at")
                    .first()
                    .changed_at.strftime("%Y-%m-%d")
                ),
            )
            self.r.set(
                "max_changed_at",
                str(
                    Event.objects.order_by("-changed_at")
                    .first()
                    .changed_at.strftime("%Y-%m-%d")
                ),
            )

        finally:
            SyncResult.objects.create(
                added_count=self.added_count, updated_count=self.updated_count
            )
            self.stdout.write(
                (
                    "Synchronization completed. "
                    f"Events added: {self.added_count}. "
                    f"Events updated: {self.updated_count}."
                )
            )
