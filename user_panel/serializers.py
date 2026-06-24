from rest_framework import serializers
from purchase.models import OrderItem, Order
from ticket.models import Ticket
from ticket.serializers import TicketMessageSerializer
from users.models import Announcement


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
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'status', 'department', 'created_at', 'updated_at', 'messages']

class DashboardAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'start_date', 'end_date', 'is_active']