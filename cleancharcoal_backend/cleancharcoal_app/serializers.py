from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]
class ProfileSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            # role/type
            "role",
            "account_type",
            # contact
            "phone",
            # picture
            "profile_picture",
            # address
            "country",
            "province",
            "district",
            "sector",
            "cell",
            "village",
            # leader jurisdiction (only if role=leader)
            "leader_district",
            "leader_sector",
            # otp status only (do NOT expose otp_code)
            "otp_verified",

            "created_at",
        ]

        # user/role/security fields cannot be edited from normal profile update
        read_only_fields = ["id", "user", "role", "otp_verified", "created_at"]

    def validate_phone(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Phone is required.")
        return value

    def validate(self, attrs):
        # If you want address to be required (recommended for burners)
        province = (attrs.get("province") or "").strip()
        district = (attrs.get("district") or "").strip()
        sector = (attrs.get("sector") or "").strip()

        # Only enforce when these fields are being updated/created through this serializer
        # (keeps PATCH flexible)
        if "province" in attrs and not province:
            raise serializers.ValidationError({"province": "Province is required."})
        if "district" in attrs and not district:
            raise serializers.ValidationError({"district": "District is required."})
        if "sector" in attrs and not sector:
            raise serializers.ValidationError({"sector": "Sector is required."})

        return attrs
