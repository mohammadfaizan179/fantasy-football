from rest_framework import serializers
from django.db import IntegrityError

from common.constants import POSITION_CHOICES
from league.models import Team, Player


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'user', 'name', 'slogan', 'capital', 'created_at', 'updated_at']
        read_only_fields = ['user', 'capital', 'created_at', 'updated_at']

    def create(self, validated_data):
        try:
            request = self.context.get("request")
            team = Team.objects.create(
                user=request.user,
                name=validated_data['name'],
                slogan=validated_data['slogan']
            )
            return team
        except IntegrityError:
            raise serializers.ValidationError({"user": ["You have already registered a team."]})

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PlayerSerializer(serializers.ModelSerializer):
    display_position = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['id', 'name', 'position', 'value', 'team', 'for_sale', 'sale_price', 'created_at', 'update_at',
                  'display_position']
        read_only_fields = ['value', 'team', 'created_at', 'update_at']

    def get_display_position(self, player):
        return POSITION_CHOICES.get(player.position)

    def create(self, validated_data):
        request = self.context.get("request")
        player = Player.objects.create(
            name=validated_data['name'],
            position=validated_data['position'],
            team=request.user.team
        )
        return player
