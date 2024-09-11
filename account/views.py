from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from account.serializers import RegisterSerializer, LoginSerializer, CustomTokenObtainPairSerializer, ProfileSerializer
from common.constants import STH_WENT_WRONG_MSG
from common.utils import generate_response


class UserRegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            return generate_response(
                message="Registration completed successfully.",
                status=status.HTTP_201_CREATED,
                data=self.serializer_class(user).data
            )
        except Exception:
            return generate_response(
                success=False,
                message=STH_WENT_WRONG_MSG,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return generate_response(
            message="Login in successfully.",
            status=status.HTTP_200_OK,
            data=serializer.validated_data
        )


class ProfileAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return generate_response(data=serializer.data)
