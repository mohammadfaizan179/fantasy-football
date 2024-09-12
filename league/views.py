import random
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from common.constants import STH_WENT_WRONG_MSG, BAD_REQUEST
from common.utils import generate_response
from league.models import Team, Player, Transaction
from league.permissions import TeamOwner, PlayerOwner
from league.serializers import TeamSerializer, PlayerSerializer, PlayerTransactionSerializer, \
    TransactionsHistorySerializer, MyTransactionsHistorySerializer


# Create your views here.
class TeamViewSet(ModelViewSet):
    serializer_class = TeamSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'destroy']:
            permission_classes = [IsAuthenticated, TeamOwner]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            team = serializer.save(request=request)
            team_data = self.get_serializer(team).data
            return generate_response(
                message="Team is created successfully.",
                status=status.HTTP_201_CREATED,
                data=team_data
            )
        except ValidationError as validation_error:
            return generate_response(
                message=BAD_REQUEST,
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                errors=validation_error.detail
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=kwargs.get('pk'))
            self.check_object_permissions(request, team)
            serializer = self.get_serializer(team, data=request.data, partial=kwargs.pop('partial', False))
            serializer.is_valid(raise_exception=True)
            team = serializer.save()
            team_data = self.get_serializer(team).data
            return generate_response(
                message="Team is updated successfully.",
                data=team_data
            )
        except Team.DoesNotExist:
            return generate_response(
                message="Team not found",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDenied, NotAuthenticated) as err:
            return generate_response(
                message=err.detail,
                success=False,
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as validation_error:
            return generate_response(
                message=BAD_REQUEST,
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                errors=validation_error.detail
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=kwargs.get('pk'))
            serializer = self.get_serializer(team)
            return generate_response(data=serializer.data)
        except Team.DoesNotExist:
            return generate_response(
                message="Team not found",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        try:
            team = Team.objects.all().order_by('-created_at')
            serializer = self.get_serializer(team, many=True)
            return generate_response(data=serializer.data)
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=kwargs.get('pk'))
            self.check_object_permissions(request, team)
            self.perform_destroy(team)
            return generate_response(
                message="Team deleted successfully",
                status=status.HTTP_204_NO_CONTENT
            )
        except Team.DoesNotExist:
            return generate_response(
                message="Team not found",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDenied, NotAuthenticated) as err:
            return generate_response(
                message=err.detail,
                success=False,
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Custom action to return login user team
    @action(
        detail=False,
        methods=['get'],
        url_path='my-team',
        url_name='my-team',
        serializer_class=TeamSerializer
    )
    def my_team(self, request):
        try:
            team = Team.objects.get(user=request.user)
            serializer = self.get_serializer(team)
            return generate_response(data=serializer.data)
        except Team.DoesNotExist:
            return generate_response(
                message="You don't have team.",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlayerViewSet(ModelViewSet):
    serializer_class = PlayerSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'destroy']:
            permission_classes = [IsAuthenticated, PlayerOwner]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            if request.user.team.players.count() >= 20:
                return generate_response(
                    message="You have already 20 players in your team. Can't add more player.",
                    success=False,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            team = serializer.save(request=request)
            team_data = self.get_serializer(team).data
            return generate_response(
                message="Player is added in your team successfully.",
                status=status.HTTP_201_CREATED,
                data=team_data
            )
        except ValidationError as validation_error:
            return generate_response(
                message=BAD_REQUEST,
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                errors=validation_error.detail
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(id=kwargs.get('pk'))
            self.check_object_permissions(request, player)
            serializer = self.get_serializer(player, data=request.data, partial=kwargs.pop('partial', False))
            serializer.is_valid(raise_exception=True)
            player = serializer.save()
            player_data = self.get_serializer(player).data
            return generate_response(
                message="Player details are updated successfully.",
                data=player_data
            )
        except Player.DoesNotExist:
            return generate_response(
                message="Player not found",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDenied, NotAuthenticated) as err:
            return generate_response(
                message=err.detail,
                success=False,
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as validation_error:
            return generate_response(
                message=BAD_REQUEST,
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                errors=validation_error.detail
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        try:
            players = Player.objects.all().order_by('-created_at')
            serializer = self.get_serializer(players, many=True)
            return generate_response(data=serializer.data)
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(id=kwargs.get('pk'))
            serializer = self.get_serializer(player)
            return generate_response(data=serializer.data)
        except Player.DoesNotExist:
            return generate_response(
                message="Player not found",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(id=kwargs.get('pk'))
            self.check_object_permissions(request, player)
            self.perform_destroy(player)
            return generate_response(
                message="Player removed from team successfully.",
                status=status.HTTP_204_NO_CONTENT
            )
        except Player.DoesNotExist:
            return generate_response(
                message="Player not found.",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDenied, NotAuthenticated) as err:
            return generate_response(
                message=err.detail,
                success=False,
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Custom action to return login user team players
    @action(
        detail=False,
        methods=['get'],
        url_path='my-team-players',
        url_name='my_team_players',
        serializer_class=PlayerSerializer
    )
    def my_team_players(self, request):
        try:
            if hasattr(request.user, 'team'):
                players = Player.objects.filter(team=request.user.team).order_by('-created_at')
                serializer = self.get_serializer(players, many=True)
                return generate_response(data=serializer.data)
            return generate_response(message="You don't have team.")
        except Exception:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SetPlayerForSaleAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, PlayerOwner]
    serializer_class = PlayerTransactionSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            player = Player.objects.get(id=kwargs.get('pk'))
            self.check_object_permissions(request, player)
            player.for_sale = True
            player.sale_price = serializer.validated_data['price']
            player.save()
            return generate_response(message="Player is set for sale.")
        except ValidationError as err:
            return generate_response(
                message=BAD_REQUEST,
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                errors=err.detail
            )
        except Player.DoesNotExist:
            return generate_response(
                message="Player not found",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDenied, NotAuthenticated) as err:
            return generate_response(
                message=err.detail,
                success=False,
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RemovePlayerFromSaleAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, PlayerOwner]

    def post(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(id=kwargs.get('pk'))
            self.check_object_permissions(request, player)
            player.for_sale = False
            player.sale_price = None
            player.save()
            return generate_response(message="Player is removed from sale.")
        except Player.DoesNotExist:
            return generate_response(
                message="Player not found",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDenied, NotAuthenticated) as err:
            return generate_response(
                message=err.detail,
                success=False,
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlayersForSaleAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PlayerSerializer

    def post(self, request, *args, **kwargs):
        try:
            players = Player.objects.filter(for_sale=True).order_by('-updated_at')
            serializer = self.get_serializer(players, many=True)
            return generate_response(data=serializer.data)
        except Exception:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BuyPlayerAPIView(generics.GenericAPIView):
    serializer_class = PlayerTransactionSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)

            buyer = request.user
            buying_price = serializer.validated_data['price']

            # Check buyer has team or not
            if not hasattr(buyer, 'team'):
                return generate_response(
                    message="You don't have team. Kindly create a team first to buy a player.",
                    success=False,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            # Get player from db
            player = Player.objects.get(id=kwargs.get('pk'))

            buyer_team = buyer.team
            seller_team = player.team

            # Check player is listed for sale
            if not player.for_sale:
                return generate_response(
                    message="Player is not listed for sale.",
                    success=False,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            # Check buyer's given price matches the players sale price
            if buying_price != player.sale_price:
                return generate_response(
                    message="Price must match the player's listed sale price.",
                    success=False,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            # Check buyer and seller is not same
            if seller_team == buyer_team:
                return generate_response(
                    message="You can't buy your own player.",
                    success=False,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            # Check buyer team's capital is sufficient to buy the player
            if buyer_team.capital < buying_price:
                return generate_response(
                    message="Your team's capital is insufficient to but this player.",
                    success=False,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            with transaction.atomic():
                # Deduct the price from buyer's team capital
                buyer_team.capital -= buying_price
                buyer_team.save()

                # Add the price to seller's team capital
                seller_team.capital += buying_price
                seller_team.save()

                # Transfer player to buyer's team
                player.team = buyer_team
                player.for_sale = False  # Mark player as not for sale anymore
                player.sale_price = None

                # Calculate a random increment between 1% and 10%
                random_increment = random.uniform(0.01, 0.10)  # Random number between 0.01 (1%) and 0.10 (10%)
                new_value = player.value * Decimal(1 + random_increment)  # Increment player value by the random percentage
                player.value = round(new_value, 2)  # Round to 2 decimal places
                player.save()

                # Record the transaction
                Transaction.objects.create(
                    buyer_team=buyer_team,
                    seller_team=seller_team,
                    player=player,
                    transfer_amount=buying_price,
                    inactive=True
                )

            return generate_response(message="Player bought successfully.")
        except ValidationError as err:
            return generate_response(
                message=BAD_REQUEST,
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                errors=err.detail
            )
        except Player.DoesNotExist:
            return generate_response(
                message="Player not found.",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionsHistoryAPIView(generics.GenericAPIView):
    serializer_class = TransactionsHistorySerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            transactions = Transaction.objects.all().order_by('-created_at')
            serializer = self.serializer_class(transactions, many=True)
            return generate_response(data=serializer.data)
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionHistoryAPIView(generics.GenericAPIView):
    serializer_class = TransactionsHistorySerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            transaction = Transaction.objects.get(id=kwargs.get('pk'))
            serializer = self.serializer_class(transaction)
            return generate_response(data=serializer.data)
        except Transaction.DoesNotExist:
            return generate_response(
                message="Transaction not found.",
                success=False,
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyTransactionsHistoryAPIView(generics.GenericAPIView):
    serializer_class = MyTransactionsHistorySerializer

    def get(self, request, *args, **kwargs):
        try:
            if hasattr(request.user, 'team'):
                transactions = Transaction.objects.filter(
                    Q(buyer_team=request.user.team) | Q(seller_team=request.user.team)
                ).order_by('-created_at').all()
                serializer = self.serializer_class(transactions, many=True, context={"request": request})
                return generate_response(data=serializer.data)
            return generate_response(message="You have not created team yet.")
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
