import random

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User
from league.models import Team, Player


# ----------- Create Fixtures ----------------

@pytest.fixture
def api_client():
    return APIClient()


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


@pytest.fixture
def auth_client(api_client, create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, user


# ----------- Create Player Test Cases ----------------
@pytest.mark.django_db
def test_player_create_success(auth_client, create_team):
    client, user = auth_client
    create_team(user)
    url = reverse('player-list')
    data = {
        'name': 'Player - 1',
        'position': 'GK'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['name'] == 'Player - 1'
    assert response.data['data']['position'] == 'GK'


@pytest.mark.django_db
def test_create_player_with_invalid_request_data(auth_client, create_team):
    client, user = auth_client
    create_team(user)
    url = reverse('player-list')

    # request param missing
    data = {
        # 'name': 'Player - 1',
        'position': 'GK'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Invalid value of request param
    data = {
        'name': 'Player - 1',
        'position': 'GKJ'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_anonymous_user_add_player(api_client):
    url = reverse('player-list')
    data = {
        'name': 'Player - 1',
        'position': 'GKJ'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_cannot_create_player_without_team(auth_client):
    client, user = auth_client
    url = reverse('player-list')
    data = {
        'name': 'Player - 1',
        'position': 'GK'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.data['message'] == "You don't have team. Create team first."


@pytest.mark.django_db
def test_team_cannot_add_more_than_20_players(auth_client, create_team, create_player):
    client, user = auth_client
    team = create_team(user)
    url = reverse('player-list')

    # Add 20 players in team
    positions = ['GK', 'DEF', 'MID', 'ATT']
    for i in range(1, 21):
        create_player(f'Player - {i}', team, positions[random.randint(0, 3)])

    data = {
        'name': 'Player - 21',
        'position': positions[random.randint(0, 3)]
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.data['message'] == "You have already 20 players in your team. Can't add more player."


# ----------- Retrieve Player Test Cases ----------------

@pytest.mark.django_db
def test_player_retrieve_success(api_client, create_user, create_team, create_player):
    user = create_user()
    team = create_team(user)
    player = create_player('Player - 1', team, 'GK')
    url = reverse('player-detail', kwargs={'pk': player.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['name'] == player.name


@pytest.mark.django_db
def test_retrieve_non_existent_player(api_client):
    url = reverse('player-detail', kwargs={'pk': 101})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == "Player not found"


# ----------- List Players Test Cases ----------------

@pytest.mark.django_db
def test_player_list_success(api_client, create_user, create_team, create_player):
    user = create_user()
    team = create_team(user)
    create_player('Player - 1', team, 'GK')
    create_player('Player - 2', team, 'DEF')

    url = reverse('player-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['data']) == 2


@pytest.mark.django_db
def test_player_list_success_empty_response(api_client, create_user, create_team):
    url = reverse('player-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['data']) == 0
    assert response.data['message'] == "success"


# ----------- Update Player Test Cases ----------------

@pytest.mark.django_db
def test_player_update_success(auth_client, create_team, create_player):
    client, user = auth_client
    team = create_team(user)
    player = create_player('Player - 1', team, 'GK')
    url = reverse('player-detail', kwargs={'pk': player.id})
    data = {'name': 'Player - 1 Updated', 'position': 'ATT'}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['name'] == 'Player - 1 Updated'
    assert response.data['data']['position'] == 'ATT'


@pytest.mark.django_db
def test_update_player_with_improper_request_data(auth_client, create_team, create_player):
    client, user = auth_client
    team = create_team(user)
    player = create_player('Player - 1', team, 'GK')
    url = reverse('player-detail', kwargs={'pk': player.id})

    # Request param is missing
    data = {
        'name': 'Player - 1 Updated',
        # 'position': 'Att',
    }
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'position' in response.data['errors']

    # Invalid request param position
    data = {
        'name': 'Player - 1 Updated',
        'position': 'At',
    }
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'position' in response.data['errors']


@pytest.mark.django_db
def test_update_non_existing_player(auth_client):
    client, user = auth_client
    url = reverse('player-detail', kwargs={'pk': 101})
    data = {
        'name': 'Player - 1 Updated',
        'position': 'Att',
    }
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == 'Player not found'


@pytest.mark.django_db
def test_update_player_of_other_team(auth_client, create_user, create_team, create_player):
    client, login_user = auth_client
    user2 = create_user('user2@gmail.com')
    team = create_team(user2)
    player = create_player('Player - 1', team, 'GK')
    url = reverse('player-detail', kwargs={'pk': player.id})
    data = {
        'name': 'Player - 1 Updated',
        'position': 'Att',
    }
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anonymous_user_update_player(api_client, create_user, create_team, create_player):
    user = create_user()
    team = create_team(user)
    player = create_player('Player - 1', team, 'GK')
    url = reverse('player-detail', kwargs={'pk': player.id})
    data = {
        'name': 'Player - 1 Updated',
        'position': 'Att',
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ----------- Delete Player Test Cases ----------------

@pytest.mark.django_db
def test_player_destroy_success(auth_client, create_team, create_player):
    client, user = auth_client
    team = create_team(user)
    player = create_player('Player - 1', team, 'GK')
    url = reverse('player-detail', kwargs={'pk': player.id})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_destroy_non_existing_team(auth_client):
    client, user = auth_client
    url = reverse('player-detail', kwargs={'pk': 101})
    response = client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == "Player not found."


@pytest.mark.django_db
def test_destroy_player_of_other_team(auth_client, create_user, create_team, create_player):
    client, login_user = auth_client
    user2 = create_user("user2#gmail.com")
    team = create_team(user2)
    player = create_player('Player - 2', team, 'GK')
    url = reverse('player-detail', kwargs={'pk': player.id})
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anonymous_user_destroying_player(api_client, create_user, create_team, create_player):
    user = create_user()
    team = create_team(user)
    player = create_player('Player - 2', team, 'GK')
    url = reverse('player-detail', kwargs={'pk': player.id})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ----------- My Players Test Cases ----------------

@pytest.mark.django_db
def test_my_team_player(auth_client, create_team, create_player):
    client, user = auth_client
    team = create_team(user)
    create_player('Player - 1', team, 'GK')
    create_player('Player - 2', team, 'ATT')
    url = reverse('player-my-team-players')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
