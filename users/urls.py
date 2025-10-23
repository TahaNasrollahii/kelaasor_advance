from django.urls import path
from .views import SendOTPView, VerifyOTPView, DashboardAPIView

app_name = "users"

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
]
