from django.urls import path
from .views import (
    UserRegisterAPIView,
    LoginAPIView
)


urlpatterns = [
    path('register/', UserRegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view())
]
