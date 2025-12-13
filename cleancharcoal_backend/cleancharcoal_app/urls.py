from django.urls import path
from .views import RegisterAPIView, VerifyOTPAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="api_verify_otp"),
]
