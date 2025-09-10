from django.contrib.auth import get_user_model
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    class Meta:
        model = get_user_model()
        fields = ("username", "password")
