from rest_framework import serializers
from .models import Ticket, TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'sender', 'sender_username', 'message', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'user', 'user_username', 'course',
                  'status', 'department', 'is_public', 'created_at', 'updated_at', 'messages']
