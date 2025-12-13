from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser

from drf_spectacular.utils import extend_schema

from .models import Profile
from .utils.otp import make_otp
from .utils.email import send_email
from .serializers_docs import RegisterRequestSerializer, VerifyOTPRequestSerializer
from .serializers import ProfileReadSerializer, ProfileUpdateSerializer
from .serializers import DeleteAccountSerializer


# ---------------------------
# REGISTER + OTP VERIFY
# ---------------------------
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

        if User.objects.filter(username=email).exists():
            return Response({"error": "An account with this email already exists."}, status=400)

        if data["password"] != data["confirm_password"]:
            return Response({"error": "Passwords do not match."}, status=400)

        otp = make_otp(5)
        subject = "CleanCharcoal - Verify your account"
        message = f"Your OTP is: {otp}"

        try:
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

                send_email(email, subject, message)

        except Exception as e:
            return Response({"error": "Registration failed. OTP could not be sent.", "details": str(e)}, status=400)

        msg = "DEV MODE: OTP printed in server terminal." if "console" in settings.EMAIL_BACKEND else "OTP sent to email."
        return Response({"message": msg, "email": email}, status=status.HTTP_201_CREATED)


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

        if not profile.otp_code or not profile.otp_created_at:
            return Response({"error": "No OTP found. Please register again."}, status=400)

        if (timezone.now() - profile.otp_created_at).total_seconds() > 600:
            return Response({"error": "OTP expired."}, status=400)

        if profile.otp_code != otp:
            return Response({"error": "Invalid OTP."}, status=400)

        profile.otp_verified = True
        profile.otp_code = None
        profile.otp_created_at = None
        profile.save()

        return Response({"message": "OTP verified successfully."}, status=200)


# ---------------------------
# MY PROFILE (GET + PATCH) ✅ Swagger file upload works here
# ---------------------------
@extend_schema(responses={200: ProfileReadSerializer}, description="Get my profile (logged-in user).")
class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ProfileReadSerializer(request.user.profile).data, status=200)


@extend_schema(
    request=ProfileUpdateSerializer,
    responses={200: ProfileReadSerializer},
    description="Update my profile (multipart/form-data for profile_picture)."
)
class ProfileUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ✅ REQUIRED

    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProfileReadSerializer(profile).data, status=200)


# ---------------------------
# FORGOT PASSWORD (OTP RESET) ✅ Fast + works with console email too
# ---------------------------
class ForgotPasswordRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={"application/json": {"type": "object", "properties": {"email": {"type": "string"}}}},
        responses={200: dict, 404: dict},
        description="Send OTP for password reset."
    )
    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"error": "Email is required."}, status=400)

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        if not hasattr(user, "profile"):
            return Response({"error": "Profile missing."}, status=400)

        otp = make_otp(5)
        user.profile.otp_code = otp
        user.profile.otp_created_at = timezone.now()
        user.profile.save()

        subject = "CleanCharcoal - Reset Password OTP"
        message = f"Your password reset OTP is: {otp}"

        try:
            send_email(email, subject, message)
        except Exception as e:
            return Response({"error": "Could not send reset OTP.", "details": str(e)}, status=400)

        msg = "DEV MODE: OTP printed in server terminal." if "console" in settings.EMAIL_BACKEND else "Reset OTP sent."
        return Response({"message": msg}, status=200)


class ForgotPasswordConfirmAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={"application/json": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "otp": {"type": "string"},
                "new_password": {"type": "string"},
                "confirm_password": {"type": "string"},
            }
        }},
        responses={200: dict, 400: dict, 404: dict},
        description="Verify OTP and set new password."
    )
    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        otp = (request.data.get("otp") or "").strip()
        new_password = request.data.get("new_password") or ""
        confirm_password = request.data.get("confirm_password") or ""

        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=400)

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=400)

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        profile = getattr(user, "profile", None)
        if not profile or not profile.otp_code or not profile.otp_created_at:
            return Response({"error": "No reset OTP found."}, status=400)

        if (timezone.now() - profile.otp_created_at).total_seconds() > 600:
            return Response({"error": "OTP expired."}, status=400)

        if profile.otp_code != otp:
            return Response({"error": "Invalid OTP."}, status=400)

        user.set_password(new_password)
        user.save()

        profile.otp_code = None
        profile.otp_created_at = None
        profile.save()

        return Response({"message": "Password reset successful."}, status=200)
@extend_schema(
    request=DeleteAccountSerializer,
    responses={204: None, 400: dict},
    description="Delete MY account (User + Profile) after password confirmation."
)
class DeleteMyAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data["password"]
        user = request.user

        # 🔐 confirm password
        if not user.check_password(password):
            return Response(
                {"error": "Incorrect password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ delete user (Profile deletes automatically via CASCADE)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)