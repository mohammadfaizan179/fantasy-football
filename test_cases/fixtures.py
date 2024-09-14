import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User
from league.models import Team, Player


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, user


@pytest.fixture
def create_user():
    def _create_user(email='user@gmail.com', first_name='User fn', last_name='User ln', password='Asdf@1122'):
        return User.objects.create_user(email=email, first_name=first_name, last_name=last_name, password=password)
    return _create_user


@pytest.fixture
def create_team():
    def _create_team(user, name='Test Team', slogan='Test Slogan'):
        return Team.objects.create(user=user, name=name, slogan=slogan)
    return _create_team


@pytest.fixture
def create_player():
    def _create_player(name, team, position='GK'):
        return Player.objects.create(name=name, position=position, team=team)
    return _create_player
