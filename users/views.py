import logging
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .services.otp_service import verify_otp, send_otp
from .throttles import OTPRateThrottle, OTPVerifyThrottle
from .utils import issue_tokens_for_user
from .serializers import (SendOTPSerializer, VerifyOTPSerializer, ForgotPasswordSendOTPSerializer,
                          ResetPasswordVerifySerializer, RegisterSerializer)


logger = logging.getLogger('users')
User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info("New user registered: %s", user.mobile)

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
    throttle_classes = [OTPRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]
        code = send_otp(mobile, purpose="login")
        logger.info("OTP sent for login: %s", mobile)

        return Response({"detail": "OTP sent successfully."}, status=200)


class VerifyOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPVerifyThrottle]

    def post(self, request):
        ser = VerifyOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        mobile = ser.validated_data["mobile"]
        code = ser.validated_data["code"]

        try:
            verify_otp(mobile, code, purpose="login")
        except ValidationError as e:
            logger.warning("OTP verification failed for %s: %s", mobile, str(e))
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(mobile=mobile)
        if user.deleted or not user.is_active:
            logger.warning("Login attempt on deactivated account: %s", mobile)
            return Response({"detail": "This account has been deactivated."}, status=status.HTTP_403_FORBIDDEN)
        tokens = issue_tokens_for_user(user)
        logger.info("User logged in via OTP: %s (created=%s)", mobile, created)

        return Response({
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {
                "id": str(user.id),
                "mobile": user.mobile,
                "full_name": user.full_name,
            }
        }, status=status.HTTP_200_OK)
    

class ForgotPasswordSendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]

        otp_code = send_otp(mobile, purpose="reset_password")
        logger.info("Password reset OTP sent for: %s", mobile)

        return Response(
            {"detail": "Reset password OTP sent successfully."},
            status=status.HTTP_200_OK
        )


class ResetPasswordVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPVerifyThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Password reset completed for: %s", request.data.get('mobile', 'unknown'))
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
