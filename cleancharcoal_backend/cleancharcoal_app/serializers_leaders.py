from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class LeaderCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    leader_district = serializers.CharField()
    leader_sector = serializers.CharField()


class LeaderUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    leader_district = serializers.CharField(required=False)
    leader_sector = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)


class AdminCreateBurnerSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()

    country = serializers.CharField(required=False, default="Rwanda")
    province = serializers.CharField()
    district = serializers.CharField()
    sector = serializers.CharField()
    cell = serializers.CharField(required=False, allow_blank=True)
    village = serializers.CharField(required=False, allow_blank=True)

    account_type = serializers.ChoiceField(
        choices=[("individual", "Individual"), ("cooperative", "Cooperative")],
        required=False,
        default="individual",
    )


class AdminUpdateBurnerSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)

    country = serializers.CharField(required=False)
    province = serializers.CharField(required=False)
    district = serializers.CharField(required=False)
    sector = serializers.CharField(required=False)
    cell = serializers.CharField(required=False, allow_blank=True)
    village = serializers.CharField(required=False, allow_blank=True)

    account_type = serializers.ChoiceField(
        choices=[("individual", "Individual"), ("cooperative", "Cooperative")],
        required=False,
    )

    password = serializers.CharField(write_only=True, required=False)
    is_active = serializers.BooleanField(required=False)
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model =User
        fields = ["id", "username", "email", "first_name", "last_name"]

class ProfileReadSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model =Profile
        fields = [
            "id", "user",
            "role", "account_type",
            "phone", "profile_picture",
            "country", "province", "district", "sector", "cell", "village",
            "leader_district", "leader_sector",
            "otp_verified", "created_at",
        ]