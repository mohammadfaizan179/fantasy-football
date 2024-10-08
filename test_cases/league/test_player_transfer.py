import random

import pytest
from django.urls import reverse
from rest_framework import status

from test_cases.fixtures import api_client, auth_client, create_user, create_team, create_player


class TestSetPlayerForSale:
    @pytest.mark.django_db
    def test_set_player_for_sale(self, auth_client, create_team, create_player):
        client, user = auth_client
        team = create_team(user)
        player = create_player('Player - 1', team, 'GK')
        url = reverse('set-player-for-sale', kwargs={'pk': player.id})
        data = {'price': 500000}
        response = client.post(url, data, format='json')
        player.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Player is set for sale.'
        assert player.for_sale is True
        assert player.sale_price == 500000

    @pytest.mark.django_db
    def test_set_player_for_sale_with_improper_request_data(self, auth_client, create_team, create_player):
        client, user = auth_client
        team = create_team(user)
        player = create_player('Player - 1', team, 'GK')
        url = reverse('set-player-for-sale', kwargs={'pk': player.id})
        data = {'wrong-key': 500000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_set_non_existing_player_for_sale(self, auth_client):
        client, user = auth_client
        url = reverse('set-player-for-sale', kwargs={'pk': 101})
        data = {'price': 500000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == 'Player not found'

    @pytest.mark.django_db
    def test_set_player_for_sale_of_other_team(self, auth_client, create_user, create_team, create_player):
        client, login_user = auth_client
        user2 = create_user('user2@gmail.com')
        team = create_team(user2)
        player = create_player('Player - 1', team, 'GK')
        url = reverse('set-player-for-sale', kwargs={'pk': player.id})
        data = {'price': 500000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_anonymous_user_set_player_for_sale(self, api_client, create_user, create_team, create_player):
        user = create_user()
        team = create_team(user)
        player = create_player('Player - 1', team, 'GK')
        url = reverse('set-player-for-sale', kwargs={'pk': player.id})
        data = {'price': 500000}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRemovePlayerFromSale:
    @pytest.mark.django_db
    def test_remove_player_from_sale(self, auth_client, create_team, create_player):
        client, user = auth_client
        team = create_team(user)
        player = create_player('Player - 1', team, 'GK')
        player.for_sale = True
        player.sale_price = 50000
        player.save()
        url = reverse('remove-player-from-sale', kwargs={'pk': player.id})
        response = client.post(url, format='json')
        player.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Player is removed from sale.'
        assert player.for_sale is False
        assert player.sale_price is None

    @pytest.mark.django_db
    def test_remove_non_existing_player_from_sale(self, auth_client):
        client, user = auth_client
        url = reverse('remove-player-from-sale', kwargs={'pk': 101})
        response = client.post(url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == 'Player not found'

    @pytest.mark.django_db
    def test_remove_player_from_sale_of_other_team(self, auth_client, create_user, create_team, create_player):
        client, login_user = auth_client
        user2 = create_user('user2@gmail.com')
        team = create_team(user2)
        player = create_player('Player - 1', team, 'GK')
        url = reverse('remove-player-from-sale', kwargs={'pk': player.id})
        response = client.post(url, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_anonymous_user_remove_player_from_sale(self, api_client, create_user, create_team, create_player):
        user = create_user()
        team = create_team(user)
        player = create_player('Player - 1', team, 'GK')
        url = reverse('remove-player-from-sale', kwargs={'pk': player.id})
        response = api_client.post(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# -------------- Players Listed For Sale Test Cases ----------------
class TestPlayerListedForSale:
    @pytest.mark.django_db
    def test_players_listed_for_sale(self, auth_client, create_user, create_team, create_player):
        client, user = auth_client
        team = create_team(user)
        player1 = create_player('Player - 1', team, 'GK')
        player1.for_sale = True
        player1.sale_price = 500000
        player1.save()

        player2 = create_player('Player - 2', team, 'ATT')
        player2.for_sale = True
        player2.sale_price = 600000
        player2.save()

        url = reverse('players-for-sale')
        response = client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2


class TestPlayerBuy:
    @pytest.mark.django_db
    def test_buy_player(self, auth_client, create_user, create_team, create_player):
        client, buyer = auth_client
        buyer_team = create_team(buyer)
        seller = create_user("user2@gmail.com")
        seller_team = create_team(seller)
        player = create_player('Player - 1', seller_team, 'GK')
        player.for_sale = True
        player.sale_price = 50000
        player.save()
        url = reverse('buy-player', kwargs={'pk': player.id})
        data = {'price': 50000}
        response = client.post(url, data, format='json')
        player.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Player bought successfully.'
        assert player.team == buyer_team

    @pytest.mark.django_db
    def test_buy_player_with_invalid_request_body(self, auth_client, create_user, create_team, create_player):
        client, buyer = auth_client
        url = reverse('buy-player', kwargs={'pk': 101})
        data = {'wrong-key': 50000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_buy_player_without_team(self, auth_client, create_user, create_team, create_player):
        client, buyer = auth_client
        url = reverse('buy-player', kwargs={'pk': 101})
        data = {'price': 50000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data['custom_code'] == 1500

    @pytest.mark.django_db
    def test_buy_non_existing_player(self, auth_client, create_user, create_team, create_player):
        client, buyer = auth_client
        buyer_team = create_team(buyer)
        url = reverse('buy-player', kwargs={'pk': 101})
        data = {'price': 50000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == 'Player not found.'

    @pytest.mark.django_db
    def test_buy_player_not_listed_for_sale(self, auth_client, create_user, create_team, create_player):
        client, buyer = auth_client
        buyer_team = create_team(buyer)
        seller = create_user("user2@gmail.com")
        seller_team = create_team(seller)
        player = create_player('Player - 1', seller_team, 'GK')
        url = reverse('buy-player', kwargs={'pk': player.id})
        data = {'price': 50000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data['custom_code'] == 1501

    @pytest.mark.django_db
    def test_buy_player_with_invalid_sale_price(self, auth_client, create_user, create_team, create_player):
        client, buyer = auth_client
        buyer_team = create_team(buyer)
        seller = create_user("user2@gmail.com")
        seller_team = create_team(seller)
        player = create_player('Player - 1', seller_team, 'GK')
        player.for_sale = True
        player.sale_price = 50000
        player.save()
        url = reverse('buy-player', kwargs={'pk': player.id})
        data = {'price': 1000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data['custom_code'] == 1502

    @pytest.mark.django_db
    def test_buy_own_team_player(self, auth_client, create_user, create_team, create_player):
        client, buyer = auth_client
        buyer_team = create_team(buyer)
        player = create_player('Player - 1', buyer_team, 'GK')
        player.for_sale = True
        player.sale_price = 50000
        player.save()
        url = reverse('buy-player', kwargs={'pk': player.id})
        data = {'price': 50000}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data['custom_code'] == 1503

    @pytest.mark.django_db
    def test_buy_player_with_insufficient_capital(self, auth_client, create_user, create_team, create_player):
        client, buyer = auth_client
        buyer_team = create_team(buyer)
        seller = create_user("user2@gmail.com")
        seller_team = create_team(seller)
        player = create_player('Player - 1', seller_team, 'GK')
        player.for_sale = True
        player.sale_price = 50000000
        player.save()
        url = reverse('buy-player', kwargs={'pk': player.id})
        data = {'price': 50000000}
        response = client.post(url, data, format='json')
        player.refresh_from_db()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data['custom_code'] == 1504


