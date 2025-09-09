from rest_framework.views import APIView
from rest_framework.response import Response
from src.auth.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST


def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return str(refresh.access_token), str(refresh)


class RegisterView(APIView):
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            access_token, refresh_token = get_tokens_for_user(user)
            data = {
                    "message": "User created successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
            status=HTTP_201_CREATED
        else:
            data = {'error': serializer.errors}
            status = HTTP_400_BAD_REQUEST
            
        return Response(data, status)
            