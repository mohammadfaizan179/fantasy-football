from rest_framework import serializers
from django.db import IntegrityError
from league.models import Team


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
