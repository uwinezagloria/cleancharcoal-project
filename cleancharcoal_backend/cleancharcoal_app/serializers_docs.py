from rest_framework import serializers


class RegisterRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

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


class VerifyOTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=5)
