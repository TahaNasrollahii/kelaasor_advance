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
    CODE_TYPE_CHOICES = [
        ('percent', 'درصدی'),
        ('fixed', 'مقدار ریالی'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=CODE_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    active_from = models.DateTimeField()
    active_until = models.DateTimeField()
    max_usage = models.PositiveIntegerField(null=True, blank=True, help_text='حداکثر تعداد استفاده کد')
    used_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text='اختصاصی به کاربر')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, help_text='اختصاصی به دوره')
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
        self.used_count += 1
        self.save()
