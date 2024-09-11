from django.urls import path
from .views import (
    UserRegisterAPIView,
    LoginAPIView, ProfileAPIView
)


urlpatterns = [
    path('register/', UserRegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('profile/', ProfileAPIView.as_view())
]
