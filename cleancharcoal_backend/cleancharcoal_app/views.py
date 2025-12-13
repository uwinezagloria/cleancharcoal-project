
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from drf_spectacular.utils import extend_schema

from .models import Profile
from .utils.otp import make_otp
from .utils.email import send_email
from .serializers_docs import RegisterRequestSerializer, VerifyOTPRequestSerializer


@extend_schema(
    request=RegisterRequestSerializer,
    responses={201: dict, 400: dict},
    description="Register burner account and send OTP (console in dev, email in prod)."
)
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data["email"].strip().lower()

        # 1. Prevent duplicates
        if User.objects.filter(username=email).exists():
            return Response(
                {"error": "An account with this email already exists."},
                status=400
            )

        # 2. Password confirmation
        if data["password"] != data["confirm_password"]:
            return Response(
                {"error": "Passwords do not match."},
                status=400
            )

        otp = make_otp(5)
        subject = "CleanCharcoal - Verify your account"
        message = f"Your OTP is: {otp}"

        try:
            # 3. Atomic transaction (all or nothing)
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=data["password"],
                    first_name=data["first_name"].strip(),
                    last_name=data["last_name"].strip(),
                )

                Profile.objects.create(
                    user=user,
                    role="burner",
                    account_type=data.get("account_type", "individual"),
                    phone=data["phone"].strip(),
                    country=data.get("country", "Rwanda"),
                    province=data["province"].strip(),
                    district=data["district"].strip(),
                    sector=data["sector"].strip(),
                    cell=(data.get("cell") or "").strip() or None,
                    village=(data.get("village") or "").strip() or None,
                    otp_code=otp,
                    otp_created_at=timezone.now(),
                    otp_verified=False,
                )

                # 4. Send OTP (console or real email depending on settings)
                send_email(email, subject, message)

        except Exception as e:
            # 5. Nothing saved if email fails
            return Response(
                {
                    "error": "Registration failed. OTP could not be sent.",
                    "details": str(e),
                },
                status=400
            )

        # 6. Honest response message
        if "console" in settings.EMAIL_BACKEND:
            msg = "DEV MODE: OTP printed in server terminal."
        else:
            msg = "Account created. OTP sent to email."

        return Response(
            {
                "message": msg,
                "email": email,
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    request=VerifyOTPRequestSerializer,
    responses={200: dict, 400: dict, 404: dict},
    description="Verify OTP and activate account."
)
class VerifyOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data["email"].strip().lower()
        otp = data["otp"].strip()

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        if not hasattr(user, "profile"):
            return Response({"error": "Profile missing."}, status=400)

        profile = user.profile

        if profile.otp_verified:
            return Response({"message": "Account already verified."}, status=200)

        if not profile.otp_code:
            return Response({"error": "No OTP found. Please register again."}, status=400)

        # OTP expiry: 10 minutes
        if (timezone.now() - profile.otp_created_at).total_seconds() > 600:
            return Response({"error": "OTP expired."}, status=400)

        if profile.otp_code != otp:
            return Response({"error": "Invalid OTP."}, status=400)

        profile.otp_verified = True
        profile.otp_code = None
        profile.otp_created_at = None
        profile.save()

        return Response(
            {"message": "OTP verified successfully."},
            status=200
        )
