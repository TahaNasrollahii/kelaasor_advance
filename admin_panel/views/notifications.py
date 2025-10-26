from rest_framework import generics, permissions
from admin_panel.models import Notification
from admin_panel.serializers.notifications import NotificationSerializer
from admin_panel.permissions import IsAdminOrSupport


class NotificationListAPIView(generics.ListAPIView):
    """
    نمایش تمام اعلان‌ها برای کاربر جاری (admin یا support)
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadAPIView(generics.UpdateAPIView):
    """
    علامت‌گذاری اعلان به عنوان خوانده شده
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]
    queryset = Notification.objects.all()
    lookup_field = 'id'

    def perform_update(self, serializer):
        serializer.save(is_read=True)
