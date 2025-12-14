from rest_framework.permissions import BasePermission
class IsAdminProfile(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "admin"
        )

class IsOTPVerified(BasePermission):
    message = "Account not verified. Please verify OTP."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and hasattr(user, "profile") and user.profile.otp_verified)
class IsBurnerProfile(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "burner"
            and request.user.profile.otp_verified is True
        )

class IsLeaderProfile(BasePermission):
    message = "Leader access only."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and hasattr(user, "profile")
            and user.profile.role == "leader"
        )        