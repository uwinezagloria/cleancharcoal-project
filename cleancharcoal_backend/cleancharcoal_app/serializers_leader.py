from rest_framework import serializers
from .models import PermissionRequest, Appointment, AppointmentReschedule


# =========================
# READ SERIALIZERS
# =========================
class LeaderPermissionReadSerializer(serializers.ModelSerializer):
    burner_email = serializers.CharField(source="burner.username", read_only=True)
    burner_first_name = serializers.CharField(source="burner.first_name", read_only=True)
    burner_last_name = serializers.CharField(source="burner.last_name", read_only=True)
    kiln_name = serializers.CharField(source="kiln.name", read_only=True)

    class Meta:
        model = PermissionRequest
        fields = [
            "id",
            "burner",
            "burner_email",
            "burner_first_name",
            "burner_last_name",
            "kiln",
            "kiln_name",
            "kiln_district",
            "kiln_sector",
            "activity_location",
            "kiln_site_name",
            "start_date",
            "end_date",
            "purpose",
            "estimated_quantity_kg",
            "message",
            "id_document",
            "land_certificate",
            "coop_certificate",
            "tree_age_proof",
            "leader_note",
            "status",
            "created_at",
            "decided_at",
        ]


class LeaderAppointmentReadSerializer(serializers.ModelSerializer):
    burner_email = serializers.CharField(source="burner.username", read_only=True)
    permission_id = serializers.IntegerField(source="permission.id", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "permission_id",
            "burner",
            "burner_email",
            "date",
            "time",
            "purpose",
            "status",
            "created_at",
        ]


class LeaderRescheduleReadSerializer(serializers.ModelSerializer):
    burner_email = serializers.CharField(source="burner.username", read_only=True)
    appointment_status = serializers.CharField(source="appointment.status", read_only=True)

    class Meta:
        model = AppointmentReschedule
        fields = [
            "id",
            "appointment",
            "appointment_status",
            "burner",
            "burner_email",
            "requested_date",
            "requested_time",
            "message",
            "status",
            "created_at",
            "resolved_at",
        ]


# =========================
# ACTION SERIALIZERS
# =========================
class LeaderPermissionDecisionSerializer(serializers.Serializer):
    # matches your PermissionRequest.STATUS_CHOICES
    decision = serializers.ChoiceField(choices=["approved", "rejected", "appointment_required"])
    leader_note = serializers.CharField(required=False, allow_blank=True)


class LeaderPermissionMessageSerializer(serializers.Serializer):
    leader_note = serializers.CharField()


class LeaderAppointmentDecisionSerializer(serializers.Serializer):
    # matches your Appointment.STATUS_CHOICES
    decision = serializers.ChoiceField(choices=["approved", "cancelled", "completed"])
    leader_note = serializers.CharField(required=False, allow_blank=True)


class LeaderAppointmentMessageSerializer(serializers.Serializer):
    leader_note = serializers.CharField()


class LeaderRescheduleDecisionSerializer(serializers.Serializer):
    # matches your AppointmentReschedule.STATUS_CHOICES
    decision = serializers.ChoiceField(choices=["accepted", "rejected"])
    leader_note = serializers.CharField(required=False, allow_blank=True)
