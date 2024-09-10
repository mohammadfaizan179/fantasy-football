from rest_framework import generics, status

from account.serializers import RegisterSerializer
from common.constants import STH_WENT_WRONG_MSG
from common.utils import generate_response


class UserRegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            data = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            message = "Registration completed successfully."
            return generate_response(
                message=message,
                status=status.HTTP_201_CREATED,
                data=data
            )
        except Exception:
            return generate_response(
                success=False,
                message=STH_WENT_WRONG_MSG,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
