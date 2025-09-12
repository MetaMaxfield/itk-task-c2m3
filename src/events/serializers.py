from rest_framework import serializers

from src.events.models import Event


class EventListSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Event
        fields = "__all__"
