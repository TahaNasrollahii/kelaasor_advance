from rest_framework import generics, permissions, status
from rest_framework.response import Response
from ticket.models import Ticket, TicketMessage
from admin_panel.permissions import IsAdminOrSupport
from admin_panel.serializers.tickets import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketReplySerializer,
)
from django.utils import timezone


class TicketListAPIView(generics.ListAPIView):
    """لیست تمام تیکت‌های کاربران"""
    serializer_class = TicketListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]

    def get_queryset(self):
        queryset = Ticket.objects.all().select_related("user").order_by("-updated_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class TicketDetailAPIView(generics.RetrieveAPIView):
    """جزئیات تیکت شامل پیام‌ها"""
    queryset = Ticket.objects.all().select_related("user").prefetch_related("messages__sender")
    serializer_class = TicketDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]
    lookup_field = "id"


class TicketReplyAPIView(generics.GenericAPIView):
    """ارسال پاسخ توسط پشتیبان"""
    serializer_class = TicketReplySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]
    queryset = Ticket.objects.all()

    def post(self, request, id):
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message_text = serializer.validated_data.get("message")
        new_status = serializer.validated_data.get("status")

        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message_text,
        )

        if new_status:
            ticket.status = new_status
        ticket.updated_at = timezone.now()
        ticket.save()

        return Response({"detail": "پاسخ ثبت شد"}, status=status.HTTP_201_CREATED)
