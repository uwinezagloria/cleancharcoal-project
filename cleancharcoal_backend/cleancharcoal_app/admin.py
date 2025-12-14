from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Profile, Kiln, Sensor, SensorData, PermissionRequest, Appointment, AppointmentReschedule


# If User is already registered, unregister first safely
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "phone", "district", "sector", "otp_verified", "created_at")
    list_filter = ("role", "otp_verified", "province", "district", "sector")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(Kiln)
class KilnAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "work_district", "work_sector", "created_at")
    list_filter = ("work_district", "work_sector")
    search_fields = ("name", "owner__username")


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("id", "sensor_type", "serial_number", "kiln", "is_active", "installed_at")
    list_filter = ("sensor_type", "is_active")
    search_fields = ("serial_number",)


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ("id", "sensor", "value", "unit", "recorded_at")
    list_filter = ("sensor__sensor_type",)
    search_fields = ("sensor__serial_number",)


@admin.register(PermissionRequest)
class PermissionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "burner", "leader", "kiln", "kiln_district", "kiln_sector", "status", "created_at")
    list_filter = ("status", "kiln_district", "kiln_sector")
    search_fields = ("burner__username", "leader__username", "kiln__name")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "leader", "burner", "permission", "date", "time", "status", "created_at")
    list_filter = ("status", "date")
    search_fields = ("leader__username", "burner__username")


@admin.register(AppointmentReschedule)
class AppointmentRescheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "burner", "leader", "requested_date", "requested_time", "status", "created_at")
    list_filter = ("status", "requested_date")
    search_fields = ("burner__username", "leader__username")
