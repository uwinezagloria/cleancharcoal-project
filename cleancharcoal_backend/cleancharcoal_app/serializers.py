from django.db import transaction
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class ProfileReadSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "role",
            "account_type",
            "phone",
            "profile_picture",
            "country",
            "province",
            "district",
            "sector",
            "cell",
            "village",
            "leader_district",
            "leader_sector",
            "otp_verified",
            "created_at",
        ]
        read_only_fields = fields


class ProfileUpdateSerializer(serializers.ModelSerializer):
    # nested user update
    user_data = UserUpdateSerializer(source="user", required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            "user_data",
            "phone",
            "profile_picture",
            "country",
            "province",
            "district",
            "sector",
            "cell",
            "village",
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        if user_data:
            user_instance = instance.user
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
            user_instance.save()

        return super().update(instance, validated_data)

    def validate_phone(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Phone is required.")
        return value


# ---------------------------
# Custom JWT Login: only verified users can login
# ---------------------------
TokenObtainPairSerializer.default_error_messages["no_active_account"] = _(
    "No account found with the given credentials."
)

class VerifiedTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not hasattr(user, "profile"):
            raise serializers.ValidationError({"detail": "Profile missing."})

        if not user.profile.otp_verified:
            raise serializers.ValidationError({"detail": "Account not verified. Verify OTP first."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Account disabled."})

        return data
class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
