from django.urls import path
from .views import (SendOTPView, VerifyOTPView,
                    ForgotPasswordSendOTPView, ResetPasswordVerifyView)

app_name = "users"

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),

    path('password/forgot/', ForgotPasswordSendOTPView.as_view(), name='forgot-password'),
    path('password/reset/', ResetPasswordVerifyView.as_view(), name='reset-password'),
]
