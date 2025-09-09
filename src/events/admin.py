from django.contrib import admin

from src.events.models import Event, Location

admin.site.register(Event)
admin.site.register(Location)
