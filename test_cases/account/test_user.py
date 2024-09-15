import pytest
from django.urls import reverse
from rest_framework import status
from test_cases.fixtures import api_client, auth_client, create_user, create_team, create_player


class TestUserRegistration:
    @pytest.mark.django_db
    def test_user_registration_success(self, api_client):
        url = reverse('user-registration')
        data = {
            'email': 'user@gmail.com',
            'first_name': 'User fn',
            'last_name': 'User ln',
            'password': 'Asdf@1122',
            'confirm_password': 'Asdf@1122'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_user_registration_with_invalid_request_body(self, api_client):
        url = reverse('user-registration')

        # Required params missing
        data = {
            'first_name': 'User fn',
            'last_name': 'User ln',
            'password': 'Asdf@1122',
            'confirm_password': 'Asdf@1122'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Required mismatch password
        data = {
            'email': 'user1@gmail.com',
            'first_name': 'User fn',
            'last_name': 'User ln',
            'password': 'Asdf@1122',
            'confirm_password': 'Asdf@1234'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_user_registration_with_duplicate_email(self, api_client, create_user):
        create_user('user@gmail.com')
        url = reverse('user-registration')
        data = {
            'email': 'user@gmail.com',
            'first_name': 'User fn',
            'last_name': 'User ln',
            'password': 'Asdf@1122',
            'confirm_password': 'Asdf@1122'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:
    @pytest.mark.django_db
    def test_user_login_success(self, api_client, create_user):
        user = create_user('user@gmail.com')
        url = reverse('user-login')
        data = {
            'email': user.email,
            'password': "Asdf@1122",
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == user.email

    @pytest.mark.django_db
    def test_user_login_with_invalid_request_body(self, api_client):
        url = reverse('user-login')
        data = {
            'wrong-email': "user@gmail.com",
            'password': "Asdf@1122",
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_user_login_with_wrong_credentials(self, api_client, create_user):
        user = create_user()
        url = reverse('user-login')
        data = {
            'email': user.email,
            'password': "WrongPassword",
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
