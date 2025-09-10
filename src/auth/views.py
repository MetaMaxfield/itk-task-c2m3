from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from src.auth.serializers import LoginSerializer, RegisterSerializer
from src.auth.services import get_tokens_for_user


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            access_token, refresh_token = get_tokens_for_user(user)
            data = {
                "message": "User created successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
            status = HTTP_201_CREATED
        else:
            data = {"error": serializer.errors}
            status = HTTP_400_BAD_REQUEST

        return Response(data, status)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token, refresh_token = get_tokens_for_user(serializer.validated_data)
        return Response(
            {"access_token": access_token, "refresh_token": refresh_token}, HTTP_200_OK
        )


class RefreshTokenView(APIView):
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            status = HTTP_200_OK
        except (AuthenticationFailed, TokenError):
            data = {"error": "Invalid or expired refresh token"}
            status = HTTP_401_UNAUTHORIZED

        return Response(data, status)
