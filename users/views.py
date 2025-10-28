from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import OTP
from .utils import issue_tokens_for_user
from .serializers import (SendOTPSerializer, VerifyOTPSerializer, ForgotPasswordSendOTPSerializer,
                          ResetPasswordVerifySerializer, RegisterSerializer)


User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "detail": "User registered successfully.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "mobile": user.mobile,
                "full_name": user.full_name,
            }
        }, status=status.HTTP_201_CREATED)


class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()
        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)



class VerifyOTPAPIView(APIView):
    """
    Verify OTP برای لاگین با موبایل + صدور توکن‌های Simple JWT
    """
    permission_classes = [permissions.AllowAny]

    OTP_TTL_MINUTES = 5       # اعتبار زمانی کد
    LOCK_MINUTES = 15         # مدت قفل بعد از بیشینه تلاش

    def post(self, request):
        ser = VerifyOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        mobile = ser.validated_data["mobile"]
        code   = ser.validated_data["code"]

        # آخرین OTP فعال برای login
        otp = get_object_or_404(
            OTP.objects.select_for_update(),
            mobile=mobile,
            purpose="login",
            is_used=False
        )

        # قفل بررسی
        now = timezone.now()
        if otp.locked_until and otp.locked_until > now:
            wait_sec = int((otp.locked_until - now).total_seconds())
            return Response(
                {"detail": "Too many attempts. Try later.", "retry_after_seconds": wait_sec},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # TTL بررسی
        if otp.created_at + timedelta(minutes=self.OTP_TTL_MINUTES) < now:
            return Response({"detail": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        # مقایسه کد
        if otp.code != code:
            # ثبت تلاش ناموفق
            otp.attempts += 1
            if otp.attempts >= otp.max_attempts:
                otp.locked_until = now + timedelta(minutes=self.LOCK_MINUTES)
            otp.save(update_fields=["attempts", "locked_until"])
            return Response({"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        # موفقیت: مصرف OTP و ریست شمارنده‌ها
        otp.is_used = True
        otp.attempts = 0
        otp.locked_until = None
        otp.save(update_fields=["is_used", "attempts", "locked_until"])

        # کاربر را پیدا/ایجاد کن (ورود با موبایل)
        user, _created = User.objects.get_or_create(
            mobile=mobile,
            defaults={"is_active": True}  # سایر فیلدها را مطابق مدل خودت مقداردهی کن
        )
        if not user.is_active:
            return Response({"detail": "User is inactive"}, status=status.HTTP_403_FORBIDDEN)

        # صدور توکن‌ها
        tokens = issue_tokens_for_user(user)

        profile = {
            "id": str(user.id),
            "mobile": user.mobile,
            "full_name": getattr(user, "full_name", None),
        }

        return Response(
            {"access": tokens["access"], "refresh": tokens["refresh"], "user": profile},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordSendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Reset password OTP sent successfully."}, status=status.HTTP_200_OK)


class ResetPasswordVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
