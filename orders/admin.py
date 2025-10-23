from django.contrib import admin
from .models import Cart, Order, OrderItem, Participant, Payment, DiscountCode



class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1
    fields = ['full_name', 'email', 'mobile']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['course', 'price', 'quantity']
    readonly_fields = ['price']
    show_change_link = True  # برای دسترسی سریع به participantها


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'discount_code', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__full_name', 'items__course__title']
    ordering = ['-created_at']
    inlines = [OrderItemInline]

    # نمایش تعداد participantها در لیست
    def participant_count(self, obj):
        return sum([item.participants.count() for item in obj.items.all()])
    participant_count.short_description = 'Participants'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'status', 'payment_date', 'transaction_id']
    list_filter = ['status', 'payment_date']
    search_fields = ['order__id', 'order__user__username', 'transaction_id']
    ordering = ['-payment_date']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__full_name']
    ordering = ['-updated_at']


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'is_active', 'used_count', 'usage_limit', 'valid_from', 'valid_to']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code', 'specific_user__username', 'specific_course__title']
