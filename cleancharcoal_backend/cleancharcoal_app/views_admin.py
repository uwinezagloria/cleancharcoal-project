from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from django.contrib.auth.models import User

from .models import Profile, PermissionRequest, Appointment, AppointmentReschedule

from .serializers_admin import (
    AdminUserReadSerializer,
    AdminLeaderCreateSerializer,
    AdminLeaderUpdateSerializer,
    AdminBurnerCreateSerializer,
    AdminBurnerUpdateSerializer,
    AdminPermissionAssignSerializer,
    AdminPermissionReadSerializer,
    AdminAppointmentReadSerializer,
    AdminRescheduleReadSerializer,
)


# =========================
# HELPERS
# =========================
def require_admin(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"error": "Authentication required."}, status=401)

    if not hasattr(request.user, "profile"):
        return Response({"error": "Profile missing for this user."}, status=400)

    if request.user.profile.role != "admin":
        return Response({"error": "Only admin can access this endpoint."}, status=403)

    return None


def _get_user_or_404(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


# =========================
# ADMIN DASHBOARD
# =========================
class AdminDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_admin(request)
        if err:
            return err

        return Response(
            {
                "counts": {
                    "users_total": User.objects.count(),
                    "leaders_total": Profile.objects.filter(role="leader").count(),
                    "burners_total": Profile.objects.filter(role="burner").count(),

                    "permissions_total": PermissionRequest.objects.count(),
                    "permissions_unassigned": PermissionRequest.objects.filter(leader__isnull=True).count(),
                    "permissions_submitted": PermissionRequest.objects.filter(status="submitted").count(),
                    "permissions_appointment_required": PermissionRequest.objects.filter(status="appointment_required").count(),
                    "permissions_approved": PermissionRequest.objects.filter(status="approved").count(),
                    "permissions_rejected": PermissionRequest.objects.filter(status="rejected").count(),

                    "appointments_total": Appointment.objects.count(),
                    "reschedules_total": AppointmentReschedule.objects.count(),
                }
            },
            status=200,
        )


# =========================
# USERS
# =========================
class AdminUserListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_admin(request)
        if err:
            return err

        qs = User.objects.select_related("profile").order_by("-id")
        return Response(AdminUserReadSerializer(qs, many=True).data, status=200)


# =========================
# LEADERS (ADMIN)
# =========================
class AdminLeaderListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_admin(request)
        if err:
            return err

        qs = User.objects.select_related("profile").filter(profile__role="leader").order_by("-id")
        return Response(AdminUserReadSerializer(qs, many=True).data, status=200)

    def post(self, request):
        err = require_admin(request)
        if err:
            return err

        s = AdminLeaderCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response({"message": "Leader created.", "leader_id": user.id}, status=201)


class AdminLeaderDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, leader_user_id):
        err = require_admin(request)
        if err:
            return err

        user = _get_user_or_404(leader_user_id)
        if not user or not hasattr(user, "profile") or user.profile.role != "leader":
            return Response({"error": "Leader not found."}, status=404)

        s = AdminLeaderUpdateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.update(user, s.validated_data)
        return Response({"message": "Leader updated."}, status=200)

    def delete(self, request, leader_user_id):
        err = require_admin(request)
        if err:
            return err

        user = _get_user_or_404(leader_user_id)
        if not user or not hasattr(user, "profile") or user.profile.role != "leader":
            return Response({"error": "Leader not found."}, status=404)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =========================
# BURNERS (ADMIN)
# =========================
class AdminBurnerCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        err = require_admin(request)
        if err:
            return err

        s = AdminBurnerCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response({"message": "Burner created.", "burner_id": user.id}, status=201)


class AdminBurnerDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        err = require_admin(request)
        if err:
            return err

        user = _get_user_or_404(user_id)
        if not user or not hasattr(user, "profile") or user.profile.role != "burner":
            return Response({"error": "Burner not found."}, status=404)

        return Response(AdminUserReadSerializer(user).data, status=200)

    def patch(self, request, user_id):
        err = require_admin(request)
        if err:
            return err

        user = _get_user_or_404(user_id)
        if not user or not hasattr(user, "profile") or user.profile.role != "burner":
            return Response({"error": "Burner not found."}, status=404)

        s = AdminBurnerUpdateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.update(user, s.validated_data)

        return Response({"message": "Burner updated."}, status=200)

    def delete(self, request, user_id):
        err = require_admin(request)
        if err:
            return err

        user = _get_user_or_404(user_id)
        if not user or not hasattr(user, "profile") or user.profile.role != "burner":
            return Response({"error": "Burner not found."}, status=404)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =========================
# PERMISSIONS (ADMIN)
# =========================
class AdminPermissionListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_admin(request)
        if err:
            return err

        qs = PermissionRequest.objects.select_related("burner", "leader", "kiln").order_by("-id")
        return Response(AdminPermissionReadSerializer(qs, many=True).data, status=200)


class AdminUnassignedPermissionListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_admin(request)
        if err:
            return err

        qs = PermissionRequest.objects.select_related("burner", "kiln").filter(leader__isnull=True).order_by("-id")
        return Response(AdminPermissionReadSerializer(qs, many=True).data, status=200)


class AdminPermissionAssignAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, permission_id):
        err = require_admin(request)
        if err:
            return err

        try:
            perm = PermissionRequest.objects.select_related("kiln").get(id=permission_id)
        except PermissionRequest.DoesNotExist:
            return Response({"error": "Permission request not found."}, status=404)

        s = AdminPermissionAssignSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        leader = _get_user_or_404(s.validated_data["leader_user_id"])
        if not leader or not hasattr(leader, "profile") or leader.profile.role != "leader":
            return Response({"error": "Leader not found."}, status=404)

        # Strong routing rule: leader jurisdiction must match permission kiln district/sector
        if (leader.profile.leader_district or "").strip().lower() != (perm.kiln_district or "").strip().lower():
            return Response({"error": "Leader district does not match permission kiln_district."}, status=400)

        if (leader.profile.leader_sector or "").strip().lower() != (perm.kiln_sector or "").strip().lower():
            return Response({"error": "Leader sector does not match permission kiln_sector."}, status=400)

        perm.leader = leader
        perm.save(update_fields=["leader"])

        return Response({"message": "Permission assigned to leader.", "leader_id": leader.id}, status=200)


# =========================
# APPOINTMENTS / RESCHEDULES (ADMIN)
# =========================
class AdminAppointmentListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_admin(request)
        if err:
            return err

        qs = Appointment.objects.select_related("leader", "burner", "permission").order_by("-id")
        return Response(AdminAppointmentReadSerializer(qs, many=True).data, status=200)


class AdminRescheduleListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_admin(request)
        if err:
            return err

        qs = AppointmentReschedule.objects.select_related("leader", "burner", "appointment").order_by("-id")
        return Response(AdminRescheduleReadSerializer(qs, many=True).data, status=200)
