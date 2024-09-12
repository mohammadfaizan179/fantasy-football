from rest_framework import serializers
from django.db import IntegrityError

from common.constants import POSITION_CHOICES
from league.models import Team, Player, Transaction


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
        fields = ['id', 'name', 'position', 'value', 'team', 'for_sale', 'sale_price', 'created_at', 'updated_at',
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


class PlayerTransactionSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)


class TransactionsHistorySerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.name')
    seller_team_name = serializers.CharField(source='seller_team.name')
    buyer_team_name = serializers.CharField(source='buyer_team.name')

    class Meta:
        model = Transaction
        fields = ['id', 'player', 'player_name', 'seller_team', 'seller_team_name', 'buyer_team', 'buyer_team_name',
                  'transfer_amount', 'completed', 'created_at']


class MyTransactionsHistorySerializer(serializers.ModelSerializer):
    my_team_role = serializers.SerializerMethodField()
    player_name = serializers.CharField(source='player.name')
    opposite_team = serializers.SerializerMethodField()

    def get_my_team_role(self, obj):
        login_user = self.context.get('request').user
        return "Seller" if login_user.team == obj.seller_team else "Buyer"

    def get_opposite_team(self, obj):
        login_user = self.context.get('request').user
        opposite_team = obj.buyer_team if login_user.team == obj.seller_team else obj.seller_team
        return {
            'id': opposite_team.id,
            'name': opposite_team.name
        }

    class Meta:
        model = Transaction
        fields = ['id', 'my_team_role', 'player', 'player_name', 'opposite_team', 'transfer_amount', 'completed',
                  'created_at']
