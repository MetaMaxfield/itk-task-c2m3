from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

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
