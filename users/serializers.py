from rest_framework import serializers
from django.utils import timezone
from orders.models import OrderItem, Order
from support.models import Ticket
from support.serializers import TicketReplySerializer
from .models import User, OTP, Announcement


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
        # TODO: ارسال پیامک از طریق سرویس third-party
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


class DashboardOrderItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['course', 'course_title', 'price', 'quantity']

class DashboardOrderSerializer(serializers.ModelSerializer):
    items = DashboardOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'status', 'discount_code', 'created_at', 'items']

class DashboardTicketSerializer(serializers.ModelSerializer):
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'status', 'department', 'created_at', 'updated_at', 'replies']

class DashboardAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'start_date', 'end_date', 'is_active']