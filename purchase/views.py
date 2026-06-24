from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from courses.models import Course
from .serializers import (
    OrderSerializer, CartItemSerializer, DiscountCodeSerializer, CheckoutSerializer
)
from .models import (Order, OrderItem, DiscountCode)
from .services.checkout_service import (
    get_pending_order,
    attach_participants_to_order,
    calculate_subtotal,
    apply_discount,
    finalize_order,
    create_payment,
    create_enrollments,
)


class CartDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        pending = Order.objects.filter(user=request.user, status='pending').first()
        if not pending:
            return Response({'items': [], 'total': 0})
        items = OrderItem.objects.filter(order=pending).select_related('course')
        total = sum(i.price * i.quantity for i in items)
        return Response({
            'order_id': pending.id,
            'items': CartItemSerializer(items, many=True).data,
            'total': total
        })


class CartAddItemAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        course = get_object_or_404(Course, id=course_id)

        if OrderItem.objects.filter(order__user=request.user, course=course, order__status='paid').exists():
            return Response({'detail': 'Course already purchased'}, status=400)

        pending_order, _ = Order.objects.get_or_create(
            user=request.user, status='pending', defaults={'total_amount': 0}
        )

        if OrderItem.objects.filter(order=pending_order, course=course).exists():
            return Response({'detail': 'Course already in cart'}, status=400)

        OrderItem.objects.create(order=pending_order, course=course, price=course.price, quantity=1)
        return Response({'detail': 'Course added to cart', 'order_id': pending_order.id}, status=201)


class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        order = get_pending_order(request.user)
        items_payload = data["items"]

        attach_participants_to_order(order, items_payload)
        subtotal = calculate_subtotal(order)

        discount_obj, discount_amount = apply_discount(order, subtotal, data.get("discount_code"))
        total = finalize_order(order, subtotal, discount_obj, discount_amount)

        create_payment(order, total)
        create_enrollments(order)

        return Response({
            "detail": "Payment successful",
            "order_id": order.id,
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "total_amount": total,
        })


class UserOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__participants', 'items__course').order_by('-created_at')


class DiscountCodeListAPIView(generics.ListAPIView):
    serializer_class = DiscountCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        return DiscountCode.objects.filter(is_active=True, active_from__lte=now, active_until__gte=now)


class ApplyDiscountCodeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        code_str = request.data.get('code')
        course_id = request.data.get('course_id')
        if not code_str or not course_id:
            return Response({'detail': 'code and course_id are required'}, status=400)

        discount = get_object_or_404(DiscountCode, code=code_str)
        course = get_object_or_404(Course, id=course_id)

        if not discount.can_use(request.user, course):
            return Response({'detail': 'Discount code is invalid or does not meet usage conditions'}, status=400)

        return Response({
            'code': discount.code,
            'discount_type': discount.discount_type,
            'value': discount.value
        }, status=200)