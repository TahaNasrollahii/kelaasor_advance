from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Ticket, TicketMessage
from .permissions import IsTicketOwnerOrSupport
from .serializers import TicketSerializer, TicketMessageSerializer
from .utils import send_ticket_reply_email, send_ticket_reply_sms


class TicketListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # کاربران فقط تیکت‌های خودشون یا عمومی را می‌بینند
        return Ticket.objects.filter(Q(user=self.request.user) | Q(is_public=True)).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # فقط کاربر خودش یا staff می‌تواند دسترسی داشته باشد
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all().order_by('-created_at')
        return Ticket.objects.filter(user=user).order_by('-created_at')


class TicketMessageCreateAPIView(generics.CreateAPIView):
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsTicketOwnerOrSupport]

    def post(self, request, *args, **kwargs):
        ticket_id = request.data.get('ticket')
        message = request.data.get('message')

        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({'detail': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

        reply = TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message
        )

        #  TODO: اطلاع‌رسانی به کاربر صاحب تیکت
        if ticket.user != request.user:
            send_ticket_reply_email(ticket.user, ticket, reply)
            send_ticket_reply_sms(ticket.user, ticket, reply)

        serializer = TicketMessageSerializer(reply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
