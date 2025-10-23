from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from courses.models import Course
from .serializers import (
    CartSerializer, OrderSerializer,
    PaymentSerializer, CartItemSerializer,
    DiscountCodeSerializer,CheckoutSerializer
)
from .models import (Cart, Order, OrderItem,
                     Participant, Payment, DiscountCode, Enrollment)



class CartDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartAddItemAPIView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        course = get_object_or_404(Course, id=course_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        # چک کنیم که قبلاً اضافه نشده باشه
        if OrderItem.objects.filter(order__user=request.user, course=course).exists():
            return Response({'detail': 'Course already purchased'}, status=status.HTTP_400_BAD_REQUEST)

        # اگر تعداد در سبد هست، اجازه تکرار ندیم
        if OrderItem.objects.filter(order__user=request.user, course=course, order__status='pending').exists():
            return Response({'detail': 'Course already in cart'}, status=status.HTTP_400_BAD_REQUEST)

        # ایجاد OrderItem موقت در سبد (pending order)
        order = Order.objects.create(user=request.user, total_amount=course.price, status='pending')
        OrderItem.objects.create(order=order, course=course, price=course.price, quantity=1)

        return Response({'detail': 'Course added to cart'}, status=status.HTTP_201_CREATED)


class CheckoutAPIView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = OrderItem.objects.filter(order__user=request.user, order__status='pending')

        if not items.exists():
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # محاسبه کل مبلغ
        total_amount = sum([item.price * item.quantity for item in items])
        order = Order.objects.create(user=request.user, total_amount=total_amount, status='paid')

        # انتقال OrderItemها به سفارش نهایی
        for item in items:
            item.order = order
            item.save()

        # خالی کردن سبد خرید
        items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class ApplyDiscountCodeAPIView(generics.GenericAPIView):
    serializer_class = DiscountCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        code_str = request.data.get('code')
        course_id = request.data.get('course_id')

        try:
            discount = DiscountCode.objects.get(code=code_str, is_active=True)
        except DiscountCode.DoesNotExist:
            return Response({'detail': 'Invalid code'}, status=400)

        # بررسی بازه زمانی
        now = timezone.now()
        if (discount.valid_from and discount.valid_from > now) or (discount.valid_to and discount.valid_to < now):
            return Response({'detail': 'Code not valid at this time'}, status=400)

        # بررسی محدودیت کاربر/دوره
        if discount.specific_user and discount.specific_user != request.user:
            return Response({'detail': 'Code not valid for this user'}, status=400)
        if discount.specific_course and str(discount.specific_course.id) != str(course_id):
            return Response({'detail': 'Code not valid for this course'}, status=400)

        # بررسی تعداد استفاده
        if discount.usage_limit and discount.used_count >= discount.usage_limit:
            return Response({'detail': 'Code usage limit reached'}, status=400)

        # اعمال تخفیف
        discount.used_count += 1
        discount.save()

        return Response({'detail': 'Discount applied', 'discount_type': discount.discount_type, 'value': discount.value})


class CheckoutAPIView(generics.GenericAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items_data = serializer.validated_data['items']
        discount_code_str = serializer.validated_data.get('discount_code')

        total_amount = 0
        discount_value = 0
        discount_type = None

        # بررسی و اعمال کد تخفیف
        discount = None
        if discount_code_str:
            try:
                discount = DiscountCode.objects.get(code=discount_code_str, is_active=True)
            except DiscountCode.DoesNotExist:
                return Response({'detail': 'Invalid discount code'}, status=400)

            now = timezone.now()
            if (discount.valid_from and discount.valid_from > now) or (discount.valid_to and discount.valid_to < now):
                return Response({'detail': 'Code not valid at this time'}, status=400)

            if discount.specific_user and discount.specific_user != request.user:
                return Response({'detail': 'Code not valid for this user'}, status=400)

        # ایجاد سفارش
        order = Order.objects.create(user=request.user, total_amount=0, status='pending')

        for item_data in items_data:
            course_id = item_data['course_id']
            participants_data = item_data.get('participants', [])

            course = Course.objects.get(id=course_id)
            price = course.price

            # محاسبه کل مبلغ
            total_amount += price * len(participants_data)

            order_item = OrderItem.objects.create(order=order, course=course, price=price,
                                                  quantity=len(participants_data))

            # ایجاد participantها و enrollment
            for participant_data in participants_data:
                participant = Participant.objects.create(order_item=order_item, **participant_data)
                Enrollment.objects.create(
                    user=request.user,
                    course=course,
                    participant=participant,
                    access_expires_at=(
                                timezone.now() + course.get_access_duration()) if course.course_type == 'offline' else None
                )

        # اعمال تخفیف
        if discount:
            discount_type = discount.discount_type
            if discount_type == 'percent':
                discount_value = total_amount * (discount.value / 100)
            else:
                discount_value = discount.value
            total_amount -= discount_value
            discount.used_count += 1
            discount.save()
            order.discount_code = discount.code

        order.total_amount = total_amount
        # TODO: اتصال به درگاه پرداخت
        order.status = 'paid'  # فرض می‌کنیم پرداخت موفق است؛ بعداً می‌توان با درگاه واقعی ادغام کرد
        order.save()

        # ثبت Payment
        Payment.objects.create(
            order=order,
            amount=total_amount,
            status='paid'
        )

        return Response({'detail': 'Checkout successful', 'order_id': order.id, 'total_amount': total_amount})