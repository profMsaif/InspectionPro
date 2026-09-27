from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "full_name",
            "phone",
            "organization",
            "role",
            "is_active",
            "is_blocked",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "role", "organization", "is_active")


class InspectionTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "blocked": "User account is blocked.",
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if getattr(self.user, "is_blocked", False) or not self.user.is_active:
            self.fail("blocked")
        return data

