from django.urls import path, include
from rest_framework.routers import DefaultRouter
from league.views import TeamViewSet, PlayerViewSet

router = DefaultRouter()
router.register("league/team", TeamViewSet, basename="team")
router.register("team/player", PlayerViewSet, basename="player")

urlpatterns = [
    path("", include(router.urls)),
]
