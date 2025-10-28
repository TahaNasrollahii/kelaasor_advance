from rest_framework import serializers
from django.utils import timezone
from .models import User, OTP
from django.contrib.auth.password_validation import validate_password


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

    def validate_mobile(self, value):
        value = value.strip()
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must include country code (e.g. +98...)")
        return value

    def create(self, validated_data):
        mobile = validated_data['mobile']

        # جلوگیری از ارسال بیش از حد
        recent_count = OTP.objects.filter(
            mobile=mobile,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
        ).count()
        if recent_count >= 5:
            raise serializers.ValidationError("Too many OTP requests. Please try again later.")

        otp = OTP.create_otp(mobile)
        # TODO: send SMS via provider
        # send_sms(mobile, f"Your verification code is {otp.code}")
        return otp


class VerifyOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        mobile = data['mobile'].strip()
        code = data['code'].strip()
        try:
            otp = OTP.objects.filter(mobile=mobile, code=code, is_used=False).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired code.")

        if otp.is_expired:
            raise serializers.ValidationError("Code expired. Please request a new one.")

        data['otp'] = otp
        return data

    def create(self, validated_data):
        otp = validated_data['otp']
        otp.mark_used()

        user, created = User.objects.get_or_create(mobile=otp.mobile)
        if created:
            user.set_unusable_password()
            user.save()

        validated_data['user'] = user
        return validated_data


class ForgotPasswordSendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)

    def validate_mobile(self, value):
        value = value.strip()
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must include country code (e.g. +98...)")
        if not User.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("No account found with this mobile.")
        return value

    def create(self, validated_data):
        mobile = validated_data['mobile']
        otp = OTP.create_otp(mobile, purpose='reset_password')
        # TODO: send SMS via provider
        # send_sms(mobile, f"Your reset password code is {otp.code}")
        return otp


class ResetPasswordVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        mobile = data['mobile'].strip()
        code = data['code'].strip()

        try:
            otp = OTP.objects.filter(
                mobile=mobile, code=code, is_used=False, purpose='reset_password'
            ).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired code.")

        if otp.is_expired:
            raise serializers.ValidationError("Code expired. Please request a new one.")

        data['otp'] = otp
        return data

    def create(self, validated_data):
        otp = validated_data['otp']
        otp.mark_used()

        user = User.objects.filter(mobile=otp.mobile).first()
        if not user:
            raise serializers.ValidationError("User not found.")

        user.set_password(validated_data['new_password'])
        user.save(update_fields=['password'])
        return user