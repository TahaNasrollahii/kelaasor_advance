from rest_framework import serializers
from purchase.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'course', 'course_title', 'price', 'quantity', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user_display', 'status', 'total_amount', 'discount_code', 'created_at', 'total_items']

    def get_total_items(self, obj):
        return obj.items.count()

    def get_user_display(self, obj):
        return obj.user.full_name or obj.user.mobile


class OrderDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'total_amount',
            'discount_code',
            'created_at',
            'updated_at',
            'items',
        ]
