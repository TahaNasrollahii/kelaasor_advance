from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    DEPARTMENT_CHOICES = [
        ('support', 'Support'),
        ('finance', 'Finance'),
        ('education', 'Education'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.sender.username} on Ticket {self.ticket.id}"
