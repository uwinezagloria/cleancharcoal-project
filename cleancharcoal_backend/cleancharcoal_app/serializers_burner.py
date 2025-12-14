from rest_framework import serializers
from .models import Profile, Kiln, PermissionRequest, Appointment, AppointmentReschedule


# =========================
# BURNER PROFILE
# =========================
class BurnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "phone",
            "profile_picture",
            "country",
            "province",
            "district",
            "sector",
            "cell",
            "village",
        ]


# =========================
# KILN
# =========================
class KilnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kiln
        fields = [
            "id",
            "name",
            "work_province",
            "work_district",
            "work_sector",
            "work_cell",
            "work_village",
            "gps_coordinates",
            "location_description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("Kiln name is required.")
        return v


# =========================
# PERMISSION REQUEST (CREATE)
# =========================
class PermissionRequestCreateSerializer(serializers.ModelSerializer):
    # docs (optional)
    id_document = serializers.FileField(required=False, allow_null=True)
    land_certificate = serializers.FileField(required=False, allow_null=True)
    coop_certificate = serializers.FileField(required=False, allow_null=True)
    tree_age_proof = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = PermissionRequest
        fields = [
            "id",

            # burner selects his kiln
            "kiln",

            # work jurisdiction (must match leader jurisdiction)
            "kiln_district",
            "kiln_sector",

            # ✅ REQUIRED application form fields
            "activity_location",
            "kiln_site_name",
            "start_date",
            "end_date",
            "purpose",
            "estimated_quantity_kg",

            # optional extra message
            "message",

            # docs
            "id_document",
            "land_certificate",
            "coop_certificate",
            "tree_age_proof",
        ]
        read_only_fields = ["id"]

    def validate_estimated_quantity_kg(self, v):
        if v is None or v <= 0:
            raise serializers.ValidationError("Estimated quantity (kg) must be greater than 0.")
        return v

    def validate(self, attrs):
        request = self.context.get("request")
        kiln = attrs.get("kiln")

        # 1) kiln must belong to logged-in burner
        if request and kiln and kiln.owner_id != request.user.id:
            raise serializers.ValidationError({"kiln": "You can only apply using your own kiln."})

        # 2) require district/sector for leader routing
        if not (attrs.get("kiln_district") or "").strip():
            raise serializers.ValidationError({"kiln_district": "Kiln district is required."})
        if not (attrs.get("kiln_sector") or "").strip():
            raise serializers.ValidationError({"kiln_sector": "Kiln sector is required."})

        # 3) validate dates
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})

        # 4) required text fields sanity
        if not (attrs.get("activity_location") or "").strip():
            raise serializers.ValidationError({"activity_location": "Activity location is required."})

        if not (attrs.get("kiln_site_name") or "").strip():
            raise serializers.ValidationError({"kiln_site_name": "Kiln site name is required."})

        if not (attrs.get("purpose") or "").strip():
            raise serializers.ValidationError({"purpose": "Purpose is required."})

        return attrs


# =========================
# PERMISSION REQUEST (READ)
# =========================
class PermissionRequestReadSerializer(serializers.ModelSerializer):
    kiln_name = serializers.CharField(source="kiln.name", read_only=True)

    class Meta:
        model = PermissionRequest
        fields = [
            "id",
            "kiln",
            "kiln_name",

            "leader",
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


# =========================
# APPOINTMENT (CREATE)
# =========================
class AppointmentCreateSerializer(serializers.Serializer):
    permission_id = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.TimeField()
    purpose = serializers.CharField()

    def validate_purpose(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("Purpose is required.")
        return v

    def validate(self, attrs):
        request = self.context.get("request")
        perm_id = attrs["permission_id"]

        try:
            perm = PermissionRequest.objects.select_related("kiln", "leader").get(id=perm_id)
        except PermissionRequest.DoesNotExist:
            raise serializers.ValidationError({"permission_id": "Permission request not found."})

        # must be yours
        if request and perm.burner_id != request.user.id:
            raise serializers.ValidationError({"permission_id": "This permission request is not yours."})

        # only if leader requested appointment
        if perm.status != "appointment_required":
            raise serializers.ValidationError({"permission_id": "Appointment is allowed only when status = appointment_required."})

        # leader must exist for appointment
        if perm.leader_id is None:
            raise serializers.ValidationError({"permission_id": "No leader assigned yet for this request."})

        attrs["permission"] = perm
        return attrs


# =========================
# RESCHEDULE (CREATE)
# =========================
class AppointmentRescheduleCreateSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField()
    requested_date = serializers.DateField()
    requested_time = serializers.TimeField()
    message = serializers.CharField()

    def validate_message(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("Message is required.")
        return v

    def validate(self, attrs):
        request = self.context.get("request")
        appt_id = attrs["appointment_id"]

        try:
            appt = Appointment.objects.select_related("leader", "burner").get(id=appt_id)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError({"appointment_id": "Appointment not found."})

        if request and appt.burner_id != request.user.id:
            raise serializers.ValidationError({"appointment_id": "This appointment is not yours."})

        attrs["appointment"] = appt
        return attrs
