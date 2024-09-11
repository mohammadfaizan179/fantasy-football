from django.urls import path
from .views import (
    UserRegisterAPIView, LoginAPIView, ProfileAPIView, ProfileUpdateAPIView
)


urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='user_registration'),
    path('login/', LoginAPIView.as_view(), name='user_login'),
    path('profile/', ProfileAPIView.as_view(), name='user_profile'),
    path('profile/update/', ProfileUpdateAPIView.as_view(), name='user_profile_update'),
]
