from django.urls import path

from .views import (
    RegisterAPIView,
    VerifyOTPAPIView,
    ProfileAPIView,
    ProfileUpdateAPIView,
    ForgotPasswordRequestAPIView,
    ForgotPasswordConfirmAPIView,
    DeleteMyAccountAPIView,
)

from .views_burner import (
    BurnerDashboardAPIView,
    BurnerProfileAPIView,
    BurnerProfileUpdateAPIView,
    BurnerDeleteAccountAPIView,
    BurnerKilnListCreateAPIView,
    BurnerKilnDetailAPIView,
    BurnerPermissionListAPIView,
    BurnerPermissionCreateAPIView,
    BurnerPermissionDetailAPIView,
    BurnerAppointmentCreateAPIView,
    BurnerRescheduleCreateAPIView,
)

from .views_leader import (
    LeaderDashboardAPIView,
    LeaderPermissionListAPIView,
    LeaderPermissionDetailAPIView,
    LeaderPermissionDecisionAPIView,
    LeaderPermissionMessageAPIView,
    LeaderAppointmentListAPIView,
    LeaderAppointmentDetailAPIView,
    LeaderAppointmentDecisionAPIView,
    LeaderAppointmentMessageAPIView,
    LeaderRescheduleListAPIView,
    LeaderRescheduleDecisionAPIView,
)

from .views_admin import (
    AdminDashboardAPIView,
    AdminUserListAPIView,
    AdminLeaderListCreateAPIView,
    AdminLeaderDetailAPIView,
    AdminBurnerCreateAPIView,
    AdminBurnerDetailAPIView,
    AdminPermissionListAPIView,
    AdminUnassignedPermissionListAPIView,
    AdminPermissionAssignAPIView,
    AdminAppointmentListAPIView,
    AdminRescheduleListAPIView,
)


urlpatterns = [
    # --- Auth / OTP ---
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="api_verify_otp"),

    # --- Profile / Password ---
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateAPIView.as_view(), name="profile_update"),
    path("profile/delete/", DeleteMyAccountAPIView.as_view(), name="delete_my_account"),
    path("password/forgot/", ForgotPasswordRequestAPIView.as_view(), name="password_forgot"),
    path("password/reset/", ForgotPasswordConfirmAPIView.as_view(), name="password_reset"),

    # --- Admin ---
    path("admin/dashboard/", AdminDashboardAPIView.as_view(), name="admin_dashboard"),
    path("admin/users/", AdminUserListAPIView.as_view(), name="admin_users"),

    path("admin/leaders/", AdminLeaderListCreateAPIView.as_view(), name="admin_leaders"),
    path("admin/leaders/<int:leader_user_id>/", AdminLeaderDetailAPIView.as_view(), name="admin_leader_detail"),

    path("admin/burners/create/", AdminBurnerCreateAPIView.as_view(), name="admin_burner_create"),
    path("admin/burners/<int:user_id>/", AdminBurnerDetailAPIView.as_view(), name="admin_burner_detail"),

    path("admin/permissions/", AdminPermissionListAPIView.as_view(), name="admin_permissions"),
    path("admin/permissions/unassigned/", AdminUnassignedPermissionListAPIView.as_view(), name="admin_permissions_unassigned"),
    path("admin/permissions/<int:permission_id>/assign/", AdminPermissionAssignAPIView.as_view(), name="admin_permission_assign"),

    path("admin/appointments/", AdminAppointmentListAPIView.as_view(), name="admin_appointments"),
    path("admin/reschedules/", AdminRescheduleListAPIView.as_view(), name="admin_reschedules"),

    # --- Burner ---
    path("burner/dashboard/", BurnerDashboardAPIView.as_view(), name="burner_dashboard"),
    path("burner/profile/", BurnerProfileAPIView.as_view(), name="burner_profile"),
    path("burner/profile/update/", BurnerProfileUpdateAPIView.as_view(), name="burner_profile_update"),
    path("burner/profile/delete/", BurnerDeleteAccountAPIView.as_view(), name="burner_delete_account"),

    path("burner/kilns/", BurnerKilnListCreateAPIView.as_view(), name="burner_kilns"),
    path("burner/kilns/<int:kiln_id>/", BurnerKilnDetailAPIView.as_view(), name="burner_kiln_detail"),

    path("burner/permissions/", BurnerPermissionListAPIView.as_view(), name="burner_permissions"),
    path("burner/permissions/create/", BurnerPermissionCreateAPIView.as_view(), name="burner_permission_create"),
    path("burner/permissions/<int:permission_id>/", BurnerPermissionDetailAPIView.as_view(), name="burner_permission_detail"),

    path("burner/appointments/create/", BurnerAppointmentCreateAPIView.as_view(), name="burner_appointment_create"),
    path("burner/appointments/reschedule/", BurnerRescheduleCreateAPIView.as_view(), name="burner_reschedule_create"),

    # --- Leader ---
    path("leader/dashboard/", LeaderDashboardAPIView.as_view(), name="leader_dashboard"),

    path("leader/permissions/", LeaderPermissionListAPIView.as_view(), name="leader_permissions"),
    path("leader/permissions/<int:permission_id>/", LeaderPermissionDetailAPIView.as_view(), name="leader_permission_detail"),
    path("leader/permissions/<int:permission_id>/decision/", LeaderPermissionDecisionAPIView.as_view(), name="leader_permission_decision"),
    path("leader/permissions/<int:permission_id>/message/", LeaderPermissionMessageAPIView.as_view(), name="leader_permission_message"),

    path("leader/appointments/", LeaderAppointmentListAPIView.as_view(), name="leader_appointments"),
    path("leader/appointments/<int:appointment_id>/", LeaderAppointmentDetailAPIView.as_view(), name="leader_appointment_detail"),
    path("leader/appointments/<int:appointment_id>/decision/", LeaderAppointmentDecisionAPIView.as_view(), name="leader_appointment_decision"),
    path("leader/appointments/<int:appointment_id>/message/", LeaderAppointmentMessageAPIView.as_view(), name="leader_appointment_message"),

    path("leader/reschedules/", LeaderRescheduleListAPIView.as_view(), name="leader_reschedules"),
    path("leader/reschedules/<int:reschedule_id>/decision/", LeaderRescheduleDecisionAPIView.as_view(), name="leader_reschedule_decision"),
]
