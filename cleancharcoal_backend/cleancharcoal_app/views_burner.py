from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from .models import Kiln, PermissionRequest, Appointment, AppointmentReschedule, Profile
from .serializers_burner import (
    BurnerProfileSerializer,
    KilnSerializer,
    PermissionRequestCreateSerializer,
    PermissionRequestReadSerializer,
    AppointmentCreateSerializer,
    AppointmentRescheduleCreateSerializer,
)


# -------------------------
# helpers
# -------------------------
def require_burner(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"error": "Authentication required."}, status=401)

    if not hasattr(request.user, "profile"):
        return Response({"error": "Profile missing for this user."}, status=400)

    if request.user.profile.role != "burner":
        return Response({"error": "Only burners can access this endpoint."}, status=403)

    return None


def require_verified_burner(request):
    err = require_burner(request)
    if err:
        return err

    if not request.user.profile.otp_verified:
        return Response({"error": "Verify your account (OTP) before continuing."}, status=403)

    return None


# -------------------------
# BURNER DASHBOARD
# -------------------------
@extend_schema(responses={200: dict})
class BurnerDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_burner(request)
        if err:
            return err

        p = request.user.profile
        return Response(
            {
                "user": {
                    "id": request.user.id,
                    "email": request.user.username,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                },
                "profile": {
                    "phone": p.phone,
                    "otp_verified": p.otp_verified,
                    "district": p.district,
                    "sector": p.sector,
                },
                "counts": {
                    "kilns": Kiln.objects.filter(owner=request.user).count(),
                    "permission_requests": PermissionRequest.objects.filter(burner=request.user).count(),
                    "appointments": Appointment.objects.filter(burner=request.user).count(),
                },
            },
            status=200,
        )


# -------------------------
# PROFILE (GET / PATCH / DELETE)
# -------------------------
@extend_schema(responses={200: BurnerProfileSerializer})
class BurnerProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_burner(request)
        if err:
            return err
        return Response(BurnerProfileSerializer(request.user.profile).data, status=200)


@extend_schema(
    methods=["PATCH"],
    request={"multipart/form-data": BurnerProfileSerializer},
    responses={200: BurnerProfileSerializer},
)
class BurnerProfileUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        err = require_burner(request)
        if err:
            return err

        s = BurnerProfileSerializer(request.user.profile, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=200)


@extend_schema(responses={204: None})
class BurnerDeleteAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        err = require_burner(request)
        if err:
            return err

        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------
# KILNS CRUD (OWNER ONLY)
# -------------------------
@extend_schema(responses={200: KilnSerializer(many=True)})
class BurnerKilnListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_burner(request)
        if err:
            return err

        qs = Kiln.objects.filter(owner=request.user).order_by("-id")
        return Response(KilnSerializer(qs, many=True).data, status=200)

    @extend_schema(request=KilnSerializer, responses={201: KilnSerializer})
    def post(self, request):
        err = require_verified_burner(request)  # burner should be verified to add official kiln
        if err:
            return err

        s = KilnSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        kiln = s.save(owner=request.user)
        return Response(KilnSerializer(kiln).data, status=201)


@extend_schema(responses={200: KilnSerializer})
class BurnerKilnDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, kiln_id):
        try:
            return Kiln.objects.get(id=kiln_id, owner=request.user)
        except Kiln.DoesNotExist:
            return None

    def get(self, request, kiln_id):
        err = require_burner(request)
        if err:
            return err

        kiln = self.get_object(request, kiln_id)
        if not kiln:
            return Response({"error": "Kiln not found."}, status=404)
        return Response(KilnSerializer(kiln).data, status=200)

    @extend_schema(request=KilnSerializer, responses={200: KilnSerializer})
    def patch(self, request, kiln_id):
        err = require_verified_burner(request)
        if err:
            return err

        kiln = self.get_object(request, kiln_id)
        if not kiln:
            return Response({"error": "Kiln not found."}, status=404)

        s = KilnSerializer(kiln, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=200)

    def delete(self, request, kiln_id):
        err = require_verified_burner(request)
        if err:
            return err

        kiln = self.get_object(request, kiln_id)
        if not kiln:
            return Response({"error": "Kiln not found."}, status=404)

        kiln.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------
# PERMISSIONS (LIST / CREATE / DETAIL)
# -------------------------
@extend_schema(responses={200: PermissionRequestReadSerializer(many=True)})
class BurnerPermissionListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        err = require_burner(request)
        if err:
            return err

        qs = PermissionRequest.objects.filter(burner=request.user).order_by("-id")
        return Response(PermissionRequestReadSerializer(qs, many=True).data, status=200)


@extend_schema(
    methods=["POST"],
    request={"multipart/form-data": PermissionRequestCreateSerializer},
    responses={201: PermissionRequestReadSerializer},
)
class BurnerPermissionCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        err = require_verified_burner(request)
        if err:
            return err

        # 1) validate form + docs
        s = PermissionRequestCreateSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)

        # 2) create as SUBMITTED (your model default is submitted)
        perm = s.save(burner=request.user, status="submitted")

        # 3) auto-assign leader based on district/sector
        kiln_district = (perm.kiln_district or "").strip()
        kiln_sector = (perm.kiln_sector or "").strip()

        leader_profile = (
            Profile.objects.select_related("user")
            .filter(
                role="leader",
                leader_district__iexact=kiln_district,
                leader_sector__iexact=kiln_sector,
            )
            .first()
        )

        if not leader_profile:
            # strong backend: fail hard (better than silent broken routing)
            perm.delete()
            return Response(
                {
                    "error": "No leader found for this district/sector.",
                    "details": {
                        "kiln_district": kiln_district,
                        "kiln_sector": kiln_sector,
                        "hint": "Admin must create a leader with matching leader_district and leader_sector.",
                    },
                },
                status=400,
            )

        perm.leader = leader_profile.user
        perm.save(update_fields=["leader"])

        return Response(PermissionRequestReadSerializer(perm).data, status=201)


@extend_schema(responses={200: PermissionRequestReadSerializer})
class BurnerPermissionDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, permission_id):
        err = require_burner(request)
        if err:
            return err

        try:
            perm = PermissionRequest.objects.get(id=permission_id, burner=request.user)
        except PermissionRequest.DoesNotExist:
            return Response({"error": "Permission request not found."}, status=404)

        return Response(PermissionRequestReadSerializer(perm).data, status=200)


# -------------------------
# APPOINTMENT (CREATE) + RESCHEDULE (CREATE)
# -------------------------
@extend_schema(request=AppointmentCreateSerializer, responses={201: dict})
class BurnerAppointmentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        err = require_verified_burner(request)
        if err:
            return err

        s = AppointmentCreateSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        perm = s.validated_data["permission"]

        # must have leader already (serializer enforces this too)
        leader_user = perm.leader

        appt = Appointment.objects.create(
            leader=leader_user,
            burner=request.user,
            permission=perm,
            date=s.validated_data["date"],
            time=s.validated_data["time"],
            purpose=s.validated_data["purpose"],
            status="pending",
        )

        return Response({"message": "Appointment requested.", "appointment_id": appt.id}, status=201)


@extend_schema(request=AppointmentRescheduleCreateSerializer, responses={201: dict})
class BurnerRescheduleCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        err = require_verified_burner(request)
        if err:
            return err

        s = AppointmentRescheduleCreateSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        appt = s.validated_data["appointment"]

        # optional extra rule: allow reschedule only if appointment is pending/approved (not completed/cancelled)
        if appt.status in ["completed", "cancelled"]:
            return Response({"error": f"Cannot reschedule an appointment that is {appt.status}."}, status=400)

        r = AppointmentReschedule.objects.create(
            appointment=appt,
            burner=request.user,
            leader=appt.leader,
            requested_date=s.validated_data["requested_date"],
            requested_time=s.validated_data["requested_time"],
            message=s.validated_data["message"],
            status="pending",
        )

        return Response({"message": "Reschedule request sent.", "reschedule_id": r.id}, status=201)
