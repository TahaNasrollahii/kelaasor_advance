from rest_framework import serializers
from .models import Ticket, TicketReply


class TicketReplySerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = TicketReply
        fields = ['id', 'ticket', 'sender', 'sender_username', 'content', 'created_at']

class TicketSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'content', 'user', 'user_username', 'course', 'status', 'department', 'is_public', 'created_at', 'updated_at', 'replies']
