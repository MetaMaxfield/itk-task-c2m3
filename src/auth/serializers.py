from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    class Meta:
        model = get_user_model()
        fields = ("username", "password")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        if not (user := authenticate(**attrs)):
            raise serializers.ValidationError({"error": "Invalid username or password"})
        return user
