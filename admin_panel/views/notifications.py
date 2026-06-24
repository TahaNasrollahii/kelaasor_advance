from rest_framework import generics, permissions
from admin_panel.models import Notification
from admin_panel.serializers.notifications import NotificationSerializer
from admin_panel.permissions import IsAdminOrSupport


class NotificationListAPIView(generics.ListAPIView):
    """List all notifications for the current user (admin or support)."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadAPIView(generics.UpdateAPIView):
    """Mark a notification as read."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]
    lookup_field = 'id'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_read=True)
