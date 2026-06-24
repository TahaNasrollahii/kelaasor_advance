from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.token_blacklist.views import (
    TokenBlacklistView,
    TokenRefreshView as BlacklistTokenRefreshView,
)
from .views import (SendOTPView, ForgotPasswordSendOTPView, ResetPasswordVerifyView,
                    RegisterView, VerifyOTPAPIView)

app_name = "users"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),

    path('password/forgot/', ForgotPasswordSendOTPView.as_view(), name='forgot-password'),
    path('password/reset/', ResetPasswordVerifyView.as_view(), name='reset-password'),
]
