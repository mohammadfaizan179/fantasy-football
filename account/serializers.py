from django.contrib.auth import authenticate
from rest_framework import serializers, status
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
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


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password']

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return {
            'access': str(token.access_token),
            'refresh': str(token)
        }

    def validate(self, attrs):
        user_obj = User.objects.filter(email=attrs.get("email").lower().strip()).first()
        if user_obj is not None:
            credentials = {
                'username': user_obj.email,
                'password': attrs.get("password")
            }
            user = authenticate(**credentials)
            if user:
                tokens = self.get_token(user)
                return {
                    "user_id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "tokens": tokens
                }
            else:
                raise serializers.ValidationError("Invalid credentials. Kindly retry with correct credentials")
        else:
            raise serializers.ValidationError({"email": "Email does not exists"}, status.HTTP_400_BAD_REQUEST)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']
