from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from account.models import User


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
        ]

    def validate(self, attrs):
        # Validate Password and confirm Passwords
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError('Password and confirm password does not match')

        # Validate email address
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': "Email already exists."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
