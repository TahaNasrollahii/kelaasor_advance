from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from courses.models import Course
from .serializers import (
    CartSerializer, OrderSerializer,
    PaymentSerializer, CartItemSerializer,
    DiscountCodeSerializer,CheckoutSerializer
)
from .models import (Cart, Order, OrderItem,
                     Participant, Payment, DiscountCode, Enrollment)



class CartDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        pending = Order.objects.filter(user=request.user, status='pending').first()
        if not pending:
            return Response({'items': [], 'total': 0})
        items = OrderItem.objects.filter(order=pending)
        total = sum(i.price * i.quantity for i in items)
        return Response({
            'order_id': pending.id,
            'items': CartItemSerializer(items, many=True).data,
            'total': total
        })


class CartAddItemAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        course = get_object_or_404(Course, id=course_id)

        # قبلاً خریده؟
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
    """
    انجام Checkout نهایی:
      - بررسی وجود سفارش pending برای کاربر
      - محاسبه مبلغ
      - اعمال کد تخفیف (در صورت وجود)
      - تغییر وضعیت سفارش به paid
      - ثبت پرداخت و enrollment
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user

        # 1. پیدا کردن سفارش pending
        order = (
            Order.objects
            .select_for_update()
            .filter(user=user, status="pending")
            .first()
        )
        if not order:
            return Response({"detail": "سبد خرید خالی است"}, status=400)

        items = list(order.items.select_related("course"))
        if not items:
            return Response({"detail": "هیچ آیتمی در سبد وجود ندارد"}, status=400)

        # 2. محاسبه مجموع قبل از تخفیف
        subtotal = sum(i.price * i.quantity for i in items)
        subtotal = Decimal(subtotal)

        discount_code = request.data.get("discount_code")
        discount_amount = Decimal("0")
        discount_obj = None

        # 3. اعمال کد تخفیف
        if discount_code:
            discount_obj = DiscountCode.objects.select_for_update().filter(code__iexact=discount_code).first()
            if not discount_obj:
                return Response({"detail": "کد تخفیف معتبر نیست"}, status=400)

            now = timezone.now()
            if not discount_obj.is_active or not (
                (discount_obj.active_from is None or now >= discount_obj.active_from)
                and (discount_obj.active_until is None or now <= discount_obj.active_until)
            ):
                return Response({"detail": "کد تخفیف منقضی یا غیرفعال است"}, status=400)

            # چک کاربر خاص
            if discount_obj.user and discount_obj.user != user:
                return Response({"detail": "کد تخفیف مخصوص کاربر دیگری است"}, status=403)

            # چک دوره خاص
            if discount_obj.course and not any(
                it.course_id == discount_obj.course_id for it in items
            ):
                return Response({"detail": "کد تخفیف برای این دوره معتبر نیست"}, status=400)

            # محاسبه مقدار تخفیف
            if discount_obj.discount_type == "percent":
                discount_amount = subtotal * Decimal(discount_obj.value) / Decimal("100")
            else:
                discount_amount = Decimal(discount_obj.value)

            # محدودسازی
            if discount_amount > subtotal:
                discount_amount = subtotal

            # افزایش شمارنده استفاده (اتمیک)
            DiscountCode.objects.filter(pk=discount_obj.pk).update(
                used_count=F("used_count") + 1
            )

        # 4. محاسبه مبلغ نهایی
        total = subtotal - discount_amount
        if total < 0:
            total = Decimal("0")

        # 5. ثبت تغییرات در Order
        order.total_amount = total
        order.status = "paid"
        if hasattr(order, "discount_code") and discount_obj:
            order.discount_code = discount_obj.code
        if hasattr(order, "discount_amount"):
            order.discount_amount = discount_amount
        order.save()

        # 6. ثبت پرداخت
        Payment.objects.create(order=order, amount=total, status="paid")

        # 7. ثبت نام کاربر در دوره‌ها
        for item in items:
            Enrollment.objects.get_or_create(user=user, course=item.course)

        return Response(
            {
                "detail": "پرداخت با موفقیت انجام شد",
                "order_id": str(order.id),
                "subtotal": str(subtotal),
                "discount_amount": str(discount_amount),
                "total_amount": str(total),
            },
            status=status.HTTP_201_CREATED,
        )



class UserOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class DiscountCodeListAPIView(generics.ListAPIView):
    serializer_class = DiscountCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # فقط کدهای فعال
        from django.utils import timezone
        now = timezone.now()
        return DiscountCode.objects.filter(is_active=True, active_from__lte=now, active_until__gte=now)


class ApplyDiscountCodeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        code_str = request.data.get('code')
        course_id = request.data.get('course_id')
        if not code_str or not course_id:
            return Response({'detail': 'code و course_id الزامی هستند'}, status=400)

        discount = get_object_or_404(DiscountCode, code=code_str)
        course = get_object_or_404(Course, id=course_id)

        if not discount.can_use(request.user, course):
            return Response({'detail': 'کد تخفیف معتبر نیست یا شرایط استفاده را ندارد'}, status=400)

        # افزایش اتمیک
        DiscountCode.objects.filter(pk=discount.pk).update(used_count=F('used_count') + 1)

        return Response({
            'code': discount.code,
            'discount_type': discount.discount_type,
            'value': discount.value
        }, status=200)


# class CheckoutAPIView(generics.GenericAPIView):
#     serializer_class = CheckoutSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         items_data = serializer.validated_data['items']
#         discount_code_str = serializer.validated_data.get('discount_code')
#
#         total_amount = 0
#         discount_value = 0
#         discount_type = None
#
#         # بررسی و اعمال کد تخفیف
#         discount = None
#         if discount_code_str:
#             try:
#                 discount = DiscountCode.objects.get(code=discount_code_str, is_active=True)
#             except DiscountCode.DoesNotExist:
#                 return Response({'detail': 'Invalid discount code'}, status=400)
#
#             now = timezone.now()
#             if (discount.valid_from and discount.valid_from > now) or (discount.valid_to and discount.valid_to < now):
#                 return Response({'detail': 'Code not valid at this time'}, status=400)
#
#             if discount.specific_user and discount.specific_user != request.user:
#                 return Response({'detail': 'Code not valid for this user'}, status=400)
#
#         # ایجاد سفارش
#         order = Order.objects.create(user=request.user, total_amount=0, status='pending')
#
#         for item_data in items_data:
#             course_id = item_data['course_id']
#             participants_data = item_data.get('participants', [])
#
#             course = Course.objects.get(id=course_id)
#             price = course.price
#
#             # محاسبه کل مبلغ
#             total_amount += price * len(participants_data)
#
#             order_item = OrderItem.objects.create(order=order, course=course, price=price,
#                                                   quantity=len(participants_data))
#
#             # ایجاد participantها و enrollment
#             for participant_data in participants_data:
#                 participant = Participant.objects.create(order_item=order_item, **participant_data)
#                 Enrollment.objects.create(
#                     user=request.user,
#                     course=course,
#                     participant=participant,
#                     access_expires_at=(
#                                 timezone.now() + course.get_access_duration()) if course.course_type == 'offline' else None
#                 )
#
#         # اعمال تخفیف
#         if discount:
#             discount_type = discount.discount_type
#             if discount_type == 'percent':
#                 discount_value = total_amount * (discount.value / 100)
#             else:
#                 discount_value = discount.value
#             total_amount -= discount_value
#             discount.used_count += 1
#             discount.save()
#             order.discount_code = discount.code
#
#         order.total_amount = total_amount
#         # TODO: اتصال به درگاه پرداخت
#         order.status = 'paid'  # فرض می‌کنیم پرداخت موفق است؛ بعداً می‌توان با درگاه واقعی ادغام کرد
#         order.save()
#
#         # ثبت Payment
#         Payment.objects.create(
#             order=order,
#             amount=total_amount,
#             status='paid'
#         )
#
#         return Response({'detail': 'Checkout successful', 'order_id': order.id, 'total_amount': total_amount})