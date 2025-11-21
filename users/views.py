from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .services.otp_service import verify_otp, generate_otp
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

        mobile = serializer.validated_data["mobile"]

        # تولید و ذخیره OTP در Redis
        otp = generate_otp(mobile, purpose="login")

        # TODO: send SMS via provider
        # send_sms(mobile, f"Your verification code is {otp}")

        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)


class VerifyOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = VerifyOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        mobile = ser.validated_data["mobile"]
        code = ser.validated_data["code"]

        try:
            verify_otp(mobile, code, purpose="login")
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # ساخت/ورود کاربر
        user, _ = User.objects.get_or_create(mobile=mobile)
        tokens = issue_tokens_for_user(user)

        return Response({
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {
                "id": str(user.id),
                "mobile": user.mobile,
                "full_name": user.full_name,
            }
        })
    

class ForgotPasswordSendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]

        otp = generate_otp(mobile, purpose="reset_password")

        # TODO: send SMS
        # send_sms(mobile, f"Your reset password code is {otp}")

        return Response({"detail": "Reset password OTP sent successfully."}, status=status.HTTP_200_OK)


class ResetPasswordVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
