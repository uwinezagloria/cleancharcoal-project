from rest_framework.permissions import BasePermission
class IsAdminProfile(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "admin"
        )
