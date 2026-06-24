from rest_framework import serializers
from .models import Ticket, TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_mobile = serializers.CharField(source='sender.mobile', read_only=True)
    sender_full_name = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'sender', 'sender_mobile', 'sender_full_name', 'message', 'created_at']
        read_only_fields = ['id', 'sender', 'sender_mobile','sender_full_name', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    user_mobile = serializers.CharField(source='user.mobile', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'user', 'user_mobile', 'user_full_name', 'course',
                  'status', 'department', 'is_public', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['user']
