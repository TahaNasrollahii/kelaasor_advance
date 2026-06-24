from rest_framework import generics, permissions
from rest_framework.response import Response
from purchase.models import Order
from ticket.models import Ticket
from users.models import Announcement
from user_panel.serializers import (DashboardOrderSerializer, DashboardTicketSerializer,
                                    DashboardAnnouncementSerializer)



class DashboardAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        orders = Order.objects.filter(user=user).prefetch_related('items__course', 'items__participants').order_by('-created_at')
        orders_data = DashboardOrderSerializer(orders, many=True).data

        tickets = Ticket.objects.filter(user=user).prefetch_related('messages__sender').order_by('-created_at')
        tickets_data = DashboardTicketSerializer(tickets, many=True).data

        announcements = Announcement.objects.filter(is_active=True).order_by('-start_date')
        announcements_data = DashboardAnnouncementSerializer(announcements, many=True).data

        return Response({
            'orders': orders_data,
            'tickets': tickets_data,
            'announcements': announcements_data
        })