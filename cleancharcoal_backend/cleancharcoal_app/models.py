from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ("burner", "Burner"),
        ("leader", "Leader"),
        ("admin", "Admin"),
    ]
    ACCOUNT_TYPES = [
        ("individual", "Individual"),
        ("cooperative", "Cooperative"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="burner")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default="individual")

    phone = models.CharField(max_length=30, default="000000000")
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    country = models.CharField(max_length=100, default="Rwanda")
    province = models.CharField(max_length=100, default="Unknown")
    district = models.CharField(max_length=100, default="Unknown")
    sector = models.CharField(max_length=100, default="Unknown")
    cell = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)

    # leader jurisdiction
    leader_district = models.CharField(max_length=100, blank=True, null=True)
    leader_sector = models.CharField(max_length=100, blank=True, null=True)

    # OTP
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Kiln(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kilns")

    name = models.CharField(max_length=200)

    # where the kiln WORK happens (can differ from burner home address)
    work_province = models.CharField(max_length=100, default="Unknown")
    work_district = models.CharField(max_length=100, default="Unknown")
    work_sector = models.CharField(max_length=100, default="Unknown")
    work_cell = models.CharField(max_length=100, blank=True, null=True)
    work_village = models.CharField(max_length=100, blank=True, null=True)

    gps_coordinates = models.CharField(max_length=100, blank=True, null=True)
    location_description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class Sensor(models.Model):
    SENSOR_TYPES = [
        ("smoke", "Smoke"),
        ("co2", "CO2"),
        ("pm25", "PM2.5"),
        ("temperature", "Temperature"),
        ("humidity", "Humidity"),
    ]

    kiln = models.ForeignKey(Kiln, on_delete=models.CASCADE, related_name="sensors")
    sensor_type = models.CharField(max_length=30, choices=SENSOR_TYPES)
    serial_number = models.CharField(max_length=100, unique=True)

    is_active = models.BooleanField(default=True)
    installed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sensor_type} - {self.serial_number}"


class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="readings")
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sensor.serial_number} -> {self.value}"


class PermissionRequest(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("appointment_required", "Appointment Required"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    burner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="permission_requests")

    # burner selects kiln (so you know exactly where he will work)
    kiln = models.ForeignKey(Kiln, on_delete=models.CASCADE, related_name="permission_requests")

    # leader assigned later (based on kiln work location)
    leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leader_permission_requests",
    )

    # leader matching based on kiln WORK location
    kiln_district = models.CharField(max_length=100)
    kiln_sector = models.CharField(max_length=100)

    # ✅ Application form fields (REQUIRED)
    activity_location = models.CharField(max_length=255)  # "Nyamagabe, ... near ..."
    kiln_site_name = models.CharField(max_length=120)     # "Kigeme Site A"
    start_date = models.DateField()
    end_date = models.DateField()
    purpose = models.TextField()
    estimated_quantity_kg = models.PositiveIntegerField()

    # optional burner extra note
    message = models.TextField(blank=True, null=True)

    # documents
    id_document = models.FileField(upload_to="docs/id/", blank=True, null=True)
    land_certificate = models.FileField(upload_to="docs/land/", blank=True, null=True)
    coop_certificate = models.FileField(upload_to="docs/coop/", blank=True, null=True)
    tree_age_proof = models.FileField(upload_to="docs/tree_age/", blank=True, null=True)

    # leader decision note
    leader_note = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="submitted")

    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"PermissionRequest #{self.id} - {self.burner.username} ({self.status})"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leader_appointments")
    burner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="burner_appointments")

    # link to permission request
    permission = models.ForeignKey(
        PermissionRequest,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    date = models.DateField()
    time = models.TimeField()
    purpose = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment #{self.id} ({self.status})"


class AppointmentReschedule(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="reschedule_requests")
    burner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reschedule_requests")
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reschedule_requests_received")

    requested_date = models.DateField()
    requested_time = models.TimeField()
    message = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reschedule #{self.id} ({self.status})"
