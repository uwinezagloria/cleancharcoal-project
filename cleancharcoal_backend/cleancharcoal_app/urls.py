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
from .views_leaders import AdminLeaderListCreateAPIView, AdminLeaderDetailAPIView,AdminUserListAPIView,AdminBurnerCreateAPIView,AdminBurnerDetailAPIView



urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="api_verify_otp"),

    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateAPIView.as_view(), name="profile_update"),
    path("profile/delete/", DeleteMyAccountAPIView.as_view(), name="delete_my_account"),
    path("password/forgot/", ForgotPasswordRequestAPIView.as_view(), name="password_forgot"),
    path("password/reset/", ForgotPasswordConfirmAPIView.as_view(), name="password_reset"),
     path("admin/leaders/", AdminLeaderListCreateAPIView.as_view(), name="admin_leaders"),
    path("admin/leaders/<int:leader_user_id>/", AdminLeaderDetailAPIView.as_view(), name="admin_leader_detail"),
     path("admin/users/", AdminUserListAPIView.as_view(), name="admin_users"),
    path("admin/burners/add/", AdminBurnerCreateAPIView.as_view(), name="admin_add_burner"),
    path("admin/burners/<int:user_id>/", AdminBurnerDetailAPIView.as_view(), name="admin_burner_detail"),
]
      

