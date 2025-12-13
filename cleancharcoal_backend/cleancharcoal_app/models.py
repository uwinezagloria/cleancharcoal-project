from django.db import models
from django.contrib.auth.models import User
# Create your models here.
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

    #  Keep NOT NULL for real requirement, but add default so migrations don’t break
    phone = models.CharField(max_length=30, default="000000000")
    #  profile picture (optional)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    #  address required, but add defaults to avoid migration prompt
    country = models.CharField(max_length=100, default="Rwanda")
    province = models.CharField(max_length=100, default="Unknown")
    district = models.CharField(max_length=100, default="Unknown")
    sector = models.CharField(max_length=100, default="Unknown")
    cell = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    # leader jurisdiction (only for leaders)
    leader_district = models.CharField(max_length=100, blank=True, null=True)
    leader_sector = models.CharField(max_length=100, blank=True, null=True)
    # OTP (system generated)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} ({self.role})"

