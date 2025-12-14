from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile, PermissionRequest, Appointment, AppointmentReschedule


# =========================
# USERS (READ)
# =========================
class AdminUserReadSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)
    otp_verified = serializers.BooleanField(source="profile.otp_verified", read_only=True)
    phone = serializers.CharField(source="profile.phone", read_only=True)
    leader_district = serializers.CharField(source="profile.leader_district", read_only=True)
    leader_sector = serializers.CharField(source="profile.leader_sector", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "is_active", "is_staff",
            "role", "otp_verified", "phone", "leader_district", "leader_sector",
        ]


# =========================
# CREATE / UPDATE LEADER
# =========================
class AdminLeaderCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    leader_district = serializers.CharField()
    leader_sector = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Username already exists."})

        if not attrs.get("leader_district", "").strip():
            raise serializers.ValidationError({"leader_district": "leader_district is required."})
        if not attrs.get("leader_sector", "").strip():
            raise serializers.ValidationError({"leader_sector": "leader_sector is required."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        # profile may be created by signal; ensure it exists
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = "leader"
        profile.phone = validated_data.get("phone") or profile.phone
        profile.leader_district = validated_data["leader_district"].strip()
        profile.leader_sector = validated_data["leader_sector"].strip()

        # Leaders should be usable immediately (admin-created)
        profile.otp_verified = True
        profile.save()

        return user


class AdminLeaderUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    leader_district = serializers.CharField(required=False, allow_blank=True)
    leader_sector = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        # instance is User
        for f in ["first_name", "last_name", "is_active"]:
            if f in validated_data:
                setattr(instance, f, validated_data[f])
        instance.save()

        profile, _ = Profile.objects.get_or_create(user=instance)
        if "phone" in validated_data:
            profile.phone = validated_data["phone"] or profile.phone
        if "leader_district" in validated_data:
            profile.leader_district = validated_data["leader_district"].strip() or profile.leader_district
        if "leader_sector" in validated_data:
            profile.leader_sector = validated_data["leader_sector"].strip() or profile.leader_sector
        profile.role = "leader"
        profile.save()

        return instance


# =========================
# CREATE / UPDATE BURNER
# =========================
class AdminBurnerCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Username already exists."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = "burner"
        if validated_data.get("phone"):
            profile.phone = validated_data["phone"]
        # burner still must verify OTP themselves (don’t auto-verify)
        profile.save()
        return user


class AdminBurnerUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    phone = serializers.CharField(required=False, allow_blank=True)
    otp_verified = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        for f in ["first_name", "last_name", "is_active"]:
            if f in validated_data:
                setattr(instance, f, validated_data[f])
        instance.save()

        profile, _ = Profile.objects.get_or_create(user=instance)
        profile.role = "burner"
        if "phone" in validated_data:
            profile.phone = validated_data["phone"] or profile.phone
        if "otp_verified" in validated_data:
            profile.otp_verified = validated_data["otp_verified"]
        profile.save()

        return instance


# =========================
# PERMISSION ASSIGN / REASSIGN
# =========================
class AdminPermissionAssignSerializer(serializers.Serializer):
    leader_user_id = serializers.IntegerField()

    def validate_leader_user_id(self, v):
        if not User.objects.filter(id=v).exists():
            raise serializers.ValidationError("Leader user not found.")
        return v


# =========================
# READ PERMISSIONS / APPTS / RESCHEDULES
# =========================
class AdminPermissionReadSerializer(serializers.ModelSerializer):
    burner_email = serializers.CharField(source="burner.username", read_only=True)
    leader_email = serializers.CharField(source="leader.username", read_only=True)
    kiln_name = serializers.CharField(source="kiln.name", read_only=True)

    class Meta:
        model = PermissionRequest
        fields = "__all__"


class AdminAppointmentReadSerializer(serializers.ModelSerializer):
    burner_email = serializers.CharField(source="burner.username", read_only=True)
    leader_email = serializers.CharField(source="leader.username", read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"


class AdminRescheduleReadSerializer(serializers.ModelSerializer):
    burner_email = serializers.CharField(source="burner.username", read_only=True)
    leader_email = serializers.CharField(source="leader.username", read_only=True)

    class Meta:
        model = AppointmentReschedule
        fields = "__all__"
