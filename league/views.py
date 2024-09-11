from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from common.constants import STH_WENT_WRONG_MSG
from common.utils import generate_response
from league.models import Team
from league.permissions import TeamOwner
from league.serializers import TeamSerializer


# Create your views here.
class TeamViewSet(ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):

        if self.action == 'update' or self.action == 'destroy':
            self.permission_classes.append(TeamOwner)
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
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
            raise
        except Exception as err:
            return generate_response(
                message=STH_WENT_WRONG_MSG,
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Custom action to return log in user team
    @action(
        detail=False,
        methods=['get'],
        url_path='myteam',
        url_name='myteam',
        serializer_class=TeamSerializer
    )
    def general_preference_card(self, request):
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

