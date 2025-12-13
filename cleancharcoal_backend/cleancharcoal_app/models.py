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

    # required for now (you can remove default later after cleaning DB)
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

