from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User
from django.contrib.auth.password_validation import validate_password
from .services.otp_service import send_otp, verify_otp


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('mobile', 'full_name', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            mobile=validated_data['mobile'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', "")
        )
        return user

class SendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)

    def create(self, validated_data):
        mobile = validated_data["mobile"]
        code = send_otp(mobile, purpose="login")
        # send_sms(mobile, f"Your code is {code}")
        return {"detail": "OTP sent"}

class VerifyOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

    def validate_mobile(self, value):
        value = value.strip()
        if not value.startswith("+"):
            raise serializers.ValidationError("Phone number must include country code (e.g. +98...)")
        return value

    def validate_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Invalid OTP format.")
        return value


class ForgotPasswordSendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)

    def validate_mobile(self, value):
        value = value.strip()
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must include country code (e.g. +98...)")
        if not User.objects.filter(mobile=value, is_active=True, deleted=False).exists():
            raise serializers.ValidationError("If an account with this mobile exists, an OTP has been sent.")
        return value

    def create(self, validated_data):
        mobile = validated_data['mobile']
        code = send_otp(mobile, purpose="reset_password")

        # TODO: send SMS
        # send_sms(mobile, f"Your reset password code is {code}")

        return {"detail": "Reset OTP sent successfully."}


class ResetPasswordVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6, validators=[validate_password])

    def validate(self, data):
        mobile = data["mobile"].strip()
        code   = data["code"].strip()

        # Validate mobile
        if not mobile.startswith("+"):
            raise serializers.ValidationError("Phone number must include country code.")

        # Validate OTP via Redis
        try:
            verify_otp(mobile, code, purpose="reset_password")
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        # Check user existence
        if not User.objects.filter(mobile=mobile, is_active=True, deleted=False).exists():
            raise serializers.ValidationError("Invalid credentials.")

        return data

    def create(self, validated_data):
        mobile = validated_data["mobile"].strip()
        new_pass = validated_data["new_password"]

        user = User.objects.get(mobile=mobile)
        user.set_password(new_pass)
        user.save(update_fields=["password"])

        return user