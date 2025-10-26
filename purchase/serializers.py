from rest_framework import serializers
from .models import (Cart, Order, OrderItem, Participant,
                     Enrollment,Payment, DiscountCode)



class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'full_name', 'email', 'mobile']


class OrderItemSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, required=False)

    class Meta:
        model = OrderItem
        fields = ['id', 'course', 'price', 'quantity', 'participants']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_amount', 'status', 'discount_code', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            participants_data = item_data.pop('participants', [])
            order_item = OrderItem.objects.create(order=order, **item_data)
            for participant_data in participants_data:
                Participant.objects.create(order_item=order_item, **participant_data)

        # بعد از ایجاد OrderItemها، می‌توان total_amount رو محاسبه کرد
        total = sum([item.price * item.quantity for item in order.items.all()])
        order.total_amount = total
        order.save()

        return order


class CartItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = OrderItem  # هر آیتم سبد خرید مشابه OrderItem
        fields = ['id', 'course', 'course_title', 'price', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, source='cart_items', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'status', 'payment_date', 'transaction_id']


class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'


class CheckoutSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(),  # هر آیتم شامل course_id و participantها
    )
    discount_code = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Cart is empty")
        for item in value:
            if 'course_id' not in item:
                raise serializers.ValidationError("Each item must have course_id")
            # بررسی شرکت‌کنندگان برای خرید گروهی
            participants = item.get('participants', [])
            if len(participants) < 1:
                raise serializers.ValidationError("Each course must have at least one participant")
        return value
