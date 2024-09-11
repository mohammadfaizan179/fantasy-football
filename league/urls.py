from django.urls import path, include
from rest_framework.routers import DefaultRouter

from league.views import TeamViewSet

router = DefaultRouter()
router.register("team", TeamViewSet, basename="team")

urlpatterns = [
    path("", include(router.urls)),
]
