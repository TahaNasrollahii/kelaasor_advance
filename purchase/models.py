from django.db import models
from django.conf import settings
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from courses.models import Course
from core.translation import (
    ORDER_STATUS_PENDING,
    ORDER_STATUS_PAID,
    ORDER_STATUS_FAILED,
    DISCOUNT_TYPE_PERCENT,
    DISCOUNT_TYPE_FIXED,
    HELP_DISCOUNT_MAX_USAGE,
    HELP_DISCOUNT_USER,
    HELP_DISCOUNT_COURSE,
)


User = settings.AUTH_USER_MODEL


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', ORDER_STATUS_PENDING),
        ('paid', ORDER_STATUS_PAID),
        ('failed', ORDER_STATUS_FAILED),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount_code = models.CharField(max_length=50, blank=True, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class Participant(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='participants')
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    participant = models.ForeignKey(Participant, on_delete=models.SET_NULL, blank=True, null=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    access_expires_at = models.DateTimeField(blank=True, null=True)


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Order.STATUS_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)


class DiscountCode(models.Model):
    CODE_TYPE_CHOICES = [
        ('percent', DISCOUNT_TYPE_PERCENT),
        ('fixed', DISCOUNT_TYPE_FIXED),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=CODE_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    active_from = models.DateTimeField()
    active_until = models.DateTimeField()
    max_usage = models.PositiveIntegerField(null=True, blank=True, help_text=HELP_DISCOUNT_MAX_USAGE)
    used_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text=HELP_DISCOUNT_USER)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, help_text=HELP_DISCOUNT_COURSE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def can_use(self, user, course):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.active_from > now or self.active_until < now:
            return False
        if self.max_usage is not None and self.used_count >= self.max_usage:
            return False
        if self.user and self.user != user:
            return False
        if self.course and self.course != course:
            return False
        return True

    def increment_usage(self):
        DiscountCode.objects.filter(pk=self.pk).update(used_count=F('used_count') + 1)
