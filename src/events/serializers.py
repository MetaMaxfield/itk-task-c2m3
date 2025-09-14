from rest_framework import serializers

from src.events.models import Event, Location


class EventListSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class LocationSyncListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        redis = self.context.get("redis")
        exists_ids = redis.smembers("exists_location_ids")

        exists_locations = []
        new_locations = []
        for val_loc_data in validated_data:
            if str(val_loc_data["id"]) in exists_ids:
                exists_locations.append(Location(**val_loc_data))
            else:
                new_locations.append(Location(**val_loc_data))

        Location.objects.bulk_create(new_locations)
        for obj_event in new_locations:
            redis.sadd("exists_location_ids", str(obj_event.id))

        Location.objects.bulk_update(
            exists_locations,
            [
                "name",
            ],
        )

        return []  # заглушка (серилизатор требует возврат значений из метода "create")


class LocationSyncSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=50)

    class Meta:
        list_serializer_class = LocationSyncListSerializer


class EventSyncListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        redis = self.context.get("redis")
        exists_ids = redis.smembers("exists_event_ids")

        exists_events = []
        new_events = []
        for val_event_data in validated_data:
            if str(val_event_data["id"]) in exists_ids:
                exists_events.append(Event(**val_event_data))
            else:
                new_events.append(Event(**val_event_data))

        Event.objects.bulk_create(new_events)
        for obj_event in new_events:
            redis.sadd("exists_event_ids", str(obj_event.id))

        Event.objects.bulk_update(
            exists_events,
            [
                "name",
                "event_time",
                "registration_deadline",
                "place",
                "status",
                "changed_at",
            ],
        )

        return len(new_events), len(exists_events)


class EventSyncSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=50)
    event_time = serializers.DateTimeField()
    registration_deadline = serializers.DateTimeField()
    place_id = serializers.UUIDField(allow_null=True)
    status = serializers.ChoiceField(
        choices=["new", "published", "registration_closed", "finished", "cancelled"]
    )
    changed_at = serializers.DateTimeField()

    def validate_status(self, value):
        closed_status = ["registration_closed", "finished", "cancelled"]
        if value in closed_status:
            return Event.CLOSED_STATUS
        return Event.OPEN_STATUS

    class Meta:
        list_serializer_class = EventSyncListSerializer
