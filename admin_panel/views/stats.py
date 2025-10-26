from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from admin_panel.permissions import IsAdminOrSupport
from users.models import User
from courses.models import Course
from purchase.models import Order, DiscountCode
from ticket.models import Ticket
from admin_panel.serializers.stats import StatsSerializer
from django.utils import timezone


class AdminStatsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]

    def get(self, request):
        now = timezone.now()
        data = {
            "total_users": User.objects.count(),
            "total_courses": Course.objects.count(),
            "total_orders": Order.objects.count(),
            "total_tickets_open": Ticket.objects.filter(status='open').count(),
            "total_tickets_in_progress": Ticket.objects.filter(status='in_progress').count(),
            "total_tickets_closed": Ticket.objects.filter(status='closed').count(),
            "total_discount_codes_active": DiscountCode.objects.filter(is_active=True, active_until__gte=now).count(),
        }
        serializer = StatsSerializer(data)
        return Response(serializer.data)
