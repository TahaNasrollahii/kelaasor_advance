from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework_simplejwt.tokens import RefreshToken
from orders.models import Order
from support.models import Ticket
from .models import Announcement
from .serializers import (SendOTPSerializer, VerifyOTPSerializer,
                          DashboardOrderSerializer, DashboardTicketSerializer,
                          DashboardAnnouncementSerializer)


class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()
        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        user = data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "mobile": user.mobile,
                "full_name": user.full_name,
            }
        })

class DashboardAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # سفارش‌ها
        orders = Order.objects.filter(user=user).order_by('-created_at')
        orders_data = DashboardOrderSerializer(orders, many=True).data

        # تیکت‌ها
        tickets = Ticket.objects.filter(user=user).order_by('-created_at')
        tickets_data = DashboardTicketSerializer(tickets, many=True).data

        # اعلان‌ها
        announcements = Announcement.objects.filter(is_active=True).order_by('-start_date')
        announcements_data = DashboardAnnouncementSerializer(announcements, many=True).data

        return Response({
            'orders': orders_data,
            'tickets': tickets_data,
            'announcements': announcements_data
        })