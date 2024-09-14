from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from account.serializers import RegisterSerializer, CustomTokenObtainPairSerializer, ProfileSerializer
from common.constants import STH_WENT_WRONG_MSG, BAD_REQUEST
from common.utils import generate_response


class UserRegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return generate_response(
                message="Registration completed successfully.",
                status=status.HTTP_201_CREATED,
                data=self.serializer_class(user).data
            )
        except ValidationError as err:
            return generate_response(
                message=BAD_REQUEST,
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                errors=err.detail
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


class ProfileUpdateAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save(request=request)
            serializer = self.serializer_class(user)
            data = {"user": serializer.data}
            return generate_response(
                message="Profile updated successfully.",
                data=data
            )
        except Exception:
            return generate_response(
                success=False,
                message=STH_WENT_WRONG_MSG,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
