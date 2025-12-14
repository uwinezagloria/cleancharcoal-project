from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import PermissionRequest, Appointment, AppointmentReschedule

from .serializers_leader import (
    LeaderPermissionReadSerializer,
    LeaderPermissionDecisionSerializer,
    LeaderPermissionMessageSerializer,
    LeaderAppointmentReadSerializer,
    LeaderAppointmentDecisionSerializer,
    LeaderAppointmentMessageSerializer,
    LeaderRescheduleReadSerializer,
    LeaderRescheduleDecisionSerializer,
)


# =========================
# HELPERS
# =========================
def require_leader(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"error": "Authentication required."}, status=401)

    if not hasattr(request.user, "profile"):
        return Response({"error": "Profile missing for this user."}, status=400)

    if request.user.profile.role != "leader":
        return Response({"error": "Only leaders can access this endpoint."}, status=403)

    return None


def _get_leader_permission_or_404(leader, permission_id):
    try:
        return PermissionRequest.objects.select_related("burner", "kiln").get(id=permission_id, leader=leader)
    except PermissionRequest.DoesNotExist:
        return None


def _get_leader_appointment_or_404(leader, appointment_id):
    try:
        return Appointment.objects.select_related("permission", "burner").get(id=appointment_id, leader=leader)
    except Appointment.DoesNotExist:
        return None


def _get_leader_reschedule_or_404(leader, reschedule_id):
    try:
        return AppointmentReschedule.objects.select_related("appointment", "burner").get(id=reschedule_id, leader=leader)
    except AppointmentReschedule.DoesNotExist:
        return None


# =========================
# LEADER DASHBOARD
# =========================
class LeaderDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_leader(request)
        if err:
            return err

        leader = request.user

        perm_qs = PermissionRequest.objects.filter(leader=leader)
        appt_qs = Appointment.objects.filter(leader=leader)
        res_qs = AppointmentReschedule.objects.filter(leader=leader)

        return Response(
            {
                "leader": {
                    "id": leader.id,
                    "email": leader.username,
                    "first_name": leader.first_name,
                    "last_name": leader.last_name,
                },
                "counts": {
                    # Permissions
                    "permission_total": perm_qs.count(),
                    "permission_submitted": perm_qs.filter(status="submitted").count(),
                    "permission_appointment_required": perm_qs.filter(status="appointment_required").count(),
                    "permission_approved": perm_qs.filter(status="approved").count(),
                    "permission_rejected": perm_qs.filter(status="rejected").count(),
                    "permission_cancelled": perm_qs.filter(status="cancelled").count(),

                    # Appointments
                    "appointments_total": appt_qs.count(),
                    "appointments_pending": appt_qs.filter(status="pending").count(),
                    "appointments_approved": appt_qs.filter(status="approved").count(),
                    "appointments_completed": appt_qs.filter(status="completed").count(),
                    "appointments_cancelled": appt_qs.filter(status="cancelled").count(),

                    # Reschedules
                    "reschedules_total": res_qs.count(),
                    "reschedules_pending": res_qs.filter(status="pending").count(),
                    "reschedules_accepted": res_qs.filter(status="accepted").count(),
                    "reschedules_rejected": res_qs.filter(status="rejected").count(),
                    "reschedules_cancelled": res_qs.filter(status="cancelled").count(),
                },
            },
            status=200,
        )


# =========================
# PERMISSIONS (LEADER)
# =========================
class LeaderPermissionListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_leader(request)
        if err:
            return err

        qs = (
            PermissionRequest.objects.filter(leader=request.user)
            .select_related("burner", "kiln")
            .order_by("-id")
        )
        return Response(LeaderPermissionReadSerializer(qs, many=True).data, status=200)


class LeaderPermissionDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, permission_id):
        err = require_leader(request)
        if err:
            return err

        perm = _get_leader_permission_or_404(request.user, permission_id)
        if not perm:
            return Response({"error": "Permission request not found."}, status=404)

        return Response(LeaderPermissionReadSerializer(perm).data, status=200)


class LeaderPermissionDecisionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, permission_id):
        err = require_leader(request)
        if err:
            return err

        perm = _get_leader_permission_or_404(request.user, permission_id)
        if not perm:
            return Response({"error": "Permission request not found."}, status=404)

        # do not decide on final states
        if perm.status in ["approved", "rejected", "cancelled"]:
            return Response({"error": f"Cannot decide on a request that is {perm.status}."}, status=400)

        s = LeaderPermissionDecisionSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        decision = s.validated_data["decision"]  # approved / rejected / appointment_required
        note = (s.validated_data.get("leader_note") or "").strip() or None

        perm.status = decision

        if note:
            perm.leader_note = note
        else:
            # strong default message
            if decision == "approved":
                perm.leader_note = perm.leader_note or "Approved by leader."
            elif decision == "rejected":
                perm.leader_note = perm.leader_note or "Rejected by leader."
            else:
                perm.leader_note = perm.leader_note or "Appointment required before approval."

        if decision in ["approved", "rejected"]:
            perm.decided_at = timezone.now()

        perm.save()
        return Response({"message": "Decision saved.", "status": perm.status}, status=200)


class LeaderPermissionMessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, permission_id):
        err = require_leader(request)
        if err:
            return err

        perm = _get_leader_permission_or_404(request.user, permission_id)
        if not perm:
            return Response({"error": "Permission request not found."}, status=404)

        s = LeaderPermissionMessageSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        perm.leader_note = s.validated_data["leader_note"].strip()
        perm.save(update_fields=["leader_note"])
        return Response({"message": "Message updated."}, status=200)


# =========================
# APPOINTMENTS (LEADER)
# =========================
class LeaderAppointmentListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_leader(request)
        if err:
            return err

        qs = (
            Appointment.objects.filter(leader=request.user)
            .select_related("permission", "burner")
            .order_by("-id")
        )
        return Response(LeaderAppointmentReadSerializer(qs, many=True).data, status=200)


class LeaderAppointmentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, appointment_id):
        err = require_leader(request)
        if err:
            return err

        appt = _get_leader_appointment_or_404(request.user, appointment_id)
        if not appt:
            return Response({"error": "Appointment not found."}, status=404)

        return Response(LeaderAppointmentReadSerializer(appt).data, status=200)


class LeaderAppointmentDecisionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, appointment_id):
        err = require_leader(request)
        if err:
            return err

        appt = _get_leader_appointment_or_404(request.user, appointment_id)
        if not appt:
            return Response({"error": "Appointment not found."}, status=404)

        # FINAL STATES: cannot change anything
        if appt.status in ["completed", "cancelled"]:
            return Response({"error": f"Cannot change an appointment that is {appt.status}."}, status=400)

        s = LeaderAppointmentDecisionSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        decision = s.validated_data["decision"]  # approved / cancelled / completed
        note = (s.validated_data.get("leader_note") or "").strip() or None

        # only allowed transitions from pending/approved
        allowed = {"pending", "approved"}
        if appt.status not in allowed:
            return Response({"error": f"Invalid appointment state: {appt.status}."}, status=400)

        appt.status = decision
        appt.save(update_fields=["status"])

        if note:
            # Keep note on the permission (single source of truth)
            appt.permission.leader_note = note
            appt.permission.save(update_fields=["leader_note"])

        return Response({"message": "Appointment updated.", "status": appt.status}, status=200)


class LeaderAppointmentMessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, appointment_id):
        err = require_leader(request)
        if err:
            return err

        appt = _get_leader_appointment_or_404(request.user, appointment_id)
        if not appt:
            return Response({"error": "Appointment not found."}, status=404)

        s = LeaderAppointmentMessageSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        appt.permission.leader_note = s.validated_data["leader_note"].strip()
        appt.permission.save(update_fields=["leader_note"])

        return Response({"message": "Message updated."}, status=200)


# =========================
# RESCHEDULES (LEADER)
# =========================
class LeaderRescheduleListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_leader(request)
        if err:
            return err

        qs = (
            AppointmentReschedule.objects.filter(leader=request.user)
            .select_related("appointment", "burner")
            .order_by("-id")
        )
        return Response(LeaderRescheduleReadSerializer(qs, many=True).data, status=200)


class LeaderRescheduleDecisionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, reschedule_id):
        err = require_leader(request)
        if err:
            return err

        r = _get_leader_reschedule_or_404(request.user, reschedule_id)
        if not r:
            return Response({"error": "Reschedule request not found."}, status=404)

        if r.status != "pending":
            return Response({"error": f"This reschedule request is already {r.status}."}, status=400)

        s = LeaderRescheduleDecisionSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        decision = s.validated_data["decision"]  # accepted / rejected
        note = (s.validated_data.get("leader_note") or "").strip() or None

        appt = r.appointment
        if appt.status in ["completed", "cancelled"]:
            return Response({"error": f"Cannot reschedule an appointment that is {appt.status}."}, status=400)

        if decision == "accepted":
            appt.date = r.requested_date
            appt.time = r.requested_time
            appt.save(update_fields=["date", "time"])

            r.status = "accepted"
            r.resolved_at = timezone.now()
            if note:
                r.message = f"{r.message}\n\n[Leader note]: {note}"
            r.save()

            return Response({"message": "Reschedule accepted. Appointment updated."}, status=200)

        # rejected
        r.status = "rejected"
        r.resolved_at = timezone.now()
        if note:
            r.message = f"{r.message}\n\n[Leader note]: {note}"
        r.save()

        return Response({"message": "Reschedule rejected."}, status=200)
