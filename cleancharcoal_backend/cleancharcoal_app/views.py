from django.contrib.auth.models import User
from django.utils import timezone

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
    responses={201: dict},
    description="Create burner account. Generates 5-digit OTP and emails it to the user."
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

        user = User.objects.create_user(
            username=email,
            email=email,
            password=data["password"],  # hashed
            first_name=data["first_name"].strip(),
            last_name=data["last_name"].strip(),
        )

        otp = make_otp(5)

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

        subject = "CleanCharcoal - Verify your account"
        message = f"Your OTP is: {otp}"

        try:
            send_email(email, subject, message)
        except Exception:
            # email can fail due to network; keep account created
            pass

        return Response(
            {"message": "Account created. OTP sent to email.", "email": email},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    request=VerifyOTPRequestSerializer,
    responses={200: dict},
    description="Verify OTP for an account."
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
            return Response({"error": "User has no profile."}, status=400)

        profile = user.profile

        if profile.otp_verified:
            return Response({"message": "Account already verified."}, status=200)

        if not profile.otp_code:
            return Response({"error": "No OTP found. Request a new one."}, status=400)

        if profile.otp_created_at and (timezone.now() - profile.otp_created_at).total_seconds() > 600:
            return Response({"error": "OTP expired. Request a new one."}, status=400)

        if profile.otp_code != otp:
            return Response({"error": "Invalid OTP."}, status=400)

        profile.otp_verified = True
        profile.otp_code = None
        profile.otp_created_at = None
        profile.save()

        return Response({"message": "OTP verified successfully."}, status=200)

