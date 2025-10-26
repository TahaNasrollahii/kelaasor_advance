from rest_framework import serializers
from ticket.models import Ticket, TicketMessage
from django.contrib.auth import get_user_model

User = get_user_model()


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = TicketMessage
        fields = ["id", "sender", "sender_username", "message", "created_at"]
        read_only_fields = ["id", "sender", "created_at"]


class TicketListSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ["id", "user_username", "subject", "status", "created_at", "updated_at", "last_message"]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        return last_msg.message if last_msg else None


class TicketDetailSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "user",
            "user_username",
            "subject",
            "status",
            "created_at",
            "updated_at",
            "messages",
        ]


class TicketReplySerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES, required=False)
