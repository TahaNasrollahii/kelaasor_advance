from django.db import models
from django.conf import settings
from courses.models import Course

User = settings.AUTH_USER_MODEL


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
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
    quantity = models.PositiveIntegerField(default=1)  # همیشه 1 برای هر کاربر
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
    access_expires_at = models.DateTimeField(blank=True, null=True)  #محدودیت دسترسی برای دوره های آنلاین


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Order.STATUS_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)


class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    discount_type = models.CharField(max_length=10, choices=[('percent', 'Percent'), ('fixed', 'Fixed')])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    usage_limit = models.PositiveIntegerField(blank=True, null=True)  # None = unlimited
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    specific_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    specific_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.code
