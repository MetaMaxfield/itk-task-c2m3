from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'password')