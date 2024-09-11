from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from common.constants import STH_WENT_WRONG_MSG, POSITION_CHOICES, BAD_REQUEST, PERMISSION_ERROR
from common.utils import generate_response
from league.models import Team, Player
from league.permissions import TeamOwner, PlayerOwner
from league.serializers import TeamSerializer, PlayerSerializer


# Create your views here.
class TeamViewSet(ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):

        if self.action == 'update' or self.action == 'destroy':
            self.permission_classes.append(TeamOwner)
        return [permission() for permission in self.permission_classes]

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
    permission_classes = [IsAuthenticated]

    def get_permissions(self):

        if self.action == 'update' or self.action == 'destroy':
            self.permission_classes.append(PlayerOwner)
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
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
            players = Player.objects.filter(team=request.user.team).order_by('-created_at')
            serializer = self.get_serializer(players, many=True)
            return generate_response(data=serializer.data)
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
