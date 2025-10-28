from django.db import models
from users.models import User

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('order', 'Order'),
        ('ticket', 'Ticket'),
        ('discount', 'Discount'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.recipient.full_name or self.recipient.mobile}"
