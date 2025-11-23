from rest_framework import serializers
from .models import Order, OrderItem, Participant, Payment, DiscountCode


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
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_amount', 'status', 'discount_code', 'created_at']
        read_only_fields = ['user', 'total_amount', 'status', 'discount_code', 'created_at']



class CartItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'course', 'course_title', 'price', 'quantity']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'status', 'payment_date', 'transaction_id']


class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'

class ParticipantInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    mobile = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)


class CheckoutItemSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    participants = ParticipantInputSerializer(many=True)

    def validate_participants(self, value):
        if not value:
            raise serializers.ValidationError("هر دوره باید حداقل یک شرکت‌کننده داشته باشد")
        return value

class CheckoutSerializer(serializers.Serializer):
    items = CheckoutItemSerializer(many=True)
    discount_code = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("سبد خرید خالی است")
        return value
