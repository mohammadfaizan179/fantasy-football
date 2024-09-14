import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User
from league.models import Team


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
def auth_client(api_client, create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, user


# ----------- Create Team Test Cases ----------------

@pytest.mark.django_db
def test_team_create_success(auth_client):
    client, user = auth_client
    url = reverse('team-list')
    data = {
        'name': 'My Team',
        'slogan': 'We are the best'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['name'] == 'My Team'
    assert response.data['data']['slogan'] == 'We are the best'


@pytest.mark.django_db
def test_create_team_with_invalid_request_data(auth_client):
    client, user = auth_client
    url = reverse('team-list')
    data = {
        # 'name' field is missing
        'slogan': 'We are the best'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_anonymous_user_create_team(api_client):
    url = reverse('team-list')
    data = {
        'name': 'My Team',
        'slogan': 'We are the best'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_cannot_create_team_if_he_has_team_already(auth_client, create_team):
    client, user = auth_client
    create_team(user)
    url = reverse('team-list')
    data = {
        'name': 'My Team',
        'slogan': 'We are the best'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['errors'] == {"user": ["You have already registered a team."]}


# ----------- Retrieve Team Test Cases ----------------

@pytest.mark.django_db
def test_team_retrieve_success(api_client, create_user, create_team):
    user = create_user()
    team = create_team(user)
    url = reverse('team-detail', kwargs={'pk': team.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['name'] == team.name


@pytest.mark.django_db
def test_retrieve_non_existent_team(api_client):
    url = reverse('team-detail', kwargs={'pk': 101})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == "Team not found"


# ----------- List Team Test Cases ----------------

@pytest.mark.django_db
def test_team_list_success(api_client, create_user, create_team):
    user1 = create_user('user1@gmail.com')
    user2 = create_user('user2@gmail.com')
    create_team(user1, name='Team 1', slogan='Team 1 slogan')
    create_team(user2, name='Team 2', slogan='Team 2 slogan')
    url = reverse('team-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['data']) == 2


@pytest.mark.django_db
def test_team_list_success_empty_response(api_client, create_user, create_team):
    url = reverse('team-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['data']) == 0
    assert response.data['message'] == "success"


# ----------- Update Team Test Cases ----------------

@pytest.mark.django_db
def test_team_update_success(auth_client, create_team):
    client, user = auth_client
    team = create_team(user)
    url = reverse('team-detail', kwargs={'pk': team.id})
    data = {'name': 'Updated Team', 'slogan': 'Updated Slogan'}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['name'] == 'Updated Team'
    assert response.data['data']['slogan'] == 'Updated Slogan'


@pytest.mark.django_db
def test_update_team_with_improper_request_data(auth_client, create_team):
    client, user = auth_client
    team = create_team(user)
    url = reverse('team-detail', kwargs={'pk': team.id})
    data = {
        'name': 'Updated Team',
        # slogan attribute is missing
    }
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'slogan' in response.data['errors']


@pytest.mark.django_db
def test_update_non_existing_team(auth_client):
    client, user = auth_client
    url = reverse('team-detail', kwargs={'pk': 101})
    data = {
        'name': 'Updated Team',
        'slogan': 'Updated Slogan'
    }
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == 'Team not found'


@pytest.mark.django_db
def test_update_team_of_other_user(auth_client, create_user, create_team):
    client, login_user = auth_client
    user2 = create_user('user2@gmail.com')
    team = create_team(user2)
    url = reverse('team-detail', kwargs={'pk': team.id})
    data = {
        'name': 'Updated Team',
        'slogan': 'Updated Slogan'
    }
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anonymous_user_update_team(api_client, create_user, create_team):
    user = create_user()
    team = create_team(user)
    url = reverse('team-detail', kwargs={'pk': team.id})
    data = {
        'name': 'Updated Team',
        'slogan': 'Updated Slogan'
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ----------- Delete Team Test Cases ----------------

@pytest.mark.django_db
def test_team_destroy_success(auth_client, create_team):
    client, user = auth_client
    team = create_team(user)
    url = reverse('team-detail', kwargs={'pk': team.id})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_destroy_non_existing_team(auth_client):
    client, user = auth_client
    url = reverse('team-detail', kwargs={'pk': 101})
    response = client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == "Team not found"


@pytest.mark.django_db
def test_destroy_team_of_other_user(auth_client, create_user, create_team):
    client, login_user = auth_client
    user2 = create_user("user2#gmail.com")
    team = create_team(user2)
    url = reverse('team-detail', kwargs={'pk': team.id})
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anonymous_user_destroying_team(api_client, create_user, create_team):
    user = create_user()
    team = create_team(user)
    url = reverse('team-detail', kwargs={'pk': team.id})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ----------- My Team Test Cases ----------------

@pytest.mark.django_db
def test_my_team(auth_client, create_team):
    client, user = auth_client
    team = create_team(user)
    url = reverse('team-my-team')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['name'] == team.name
