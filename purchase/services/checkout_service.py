from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import ValidationError
from ..models import (
    Order,
    OrderItem,
    Participant,
    DiscountCode,
    Payment,
    Enrollment,
)


def get_pending_order(user: "User") -> Order:
    """
    برگرداندن سفارش pending کاربر با قفل جهت عملیات اتمیک.
    """
    order = (
        Order.objects
        .select_for_update()
        .filter(user=user, status="pending")
        .first()
    )
    if not order:
        raise ValidationError({"detail": "سبد خرید خالی است"})

    if not order.items.exists():
        raise ValidationError({"detail": "هیچ آیتمی در سبد وجود ندارد"})

    return order


def attach_participants_to_order(order: Order, items_payload: list[dict]) -> None:
    """
    participants را به OrderItemهای مربوط وصل می‌کند و quantity را آپدیت می‌کند.
    items_payload ساختاری مثل:
    [
      {
        "course_id": 3,
        "participants": [
          {"full_name": "...", "email": "...", "mobile": "..."},
          ...
        ]
      },
      ...
    ]
    دارد (قبلاً توسط CheckoutSerializer اعتبارسنجی شده).
    """
    # آیتم‌های سبد
    order_items = list(order.items.select_related("course"))

    # course_id -> participants list
    participants_by_course = {
        item["course_id"]: item["participants"]
        for item in items_payload
    }

    # دوره‌ای در سبد هست ولی در payload نیست
    for order_item in order_items:
        if order_item.course_id not in participants_by_course:
            raise ValidationError({
                "detail": f"برای دوره‌ی با شناسه {order_item.course_id} شرکت‌کننده‌ای ارسال نشده است"
            })

    # دوره‌ای در payload هست ولی در سبد نیست
    course_ids_in_cart = {item.course_id for item in order_items}
    for course_id in participants_by_course.keys():
        if course_id not in course_ids_in_cart:
            raise ValidationError({
                "detail": f"دوره‌ی با شناسه {course_id} در سبد خرید شما وجود ندارد"
            })

    # ساخت/به‌روزرسانی participants و quantity
    for order_item in order_items:
        participants_data = participants_by_course[order_item.course_id]

        # پاک کردن شرکت‌کننده‌های قبلی این آیتم
        order_item.participants.all().delete()

        # ساخت شرکت‌کننده‌ها
        for p in participants_data:
            Participant.objects.create(
                order_item=order_item,
                full_name=p["full_name"],
                email=p.get("email"),
                mobile=p.get("mobile"),
            )

        # quantity = تعداد شرکت‌کننده‌ها
        order_item.quantity = len(participants_data)
        order_item.save()


def calculate_subtotal(order: Order) -> Decimal:
    """
    جمع مبلغ قبل از تخفیف (price * quantity برای هر آیتم).
    """
    items = order.items.all()
    subtotal = sum((item.price * item.quantity for item in items), Decimal("0"))
    return subtotal


def apply_discount(
    order: Order,
    subtotal: Decimal,
    discount_code: str | None,
) -> tuple[DiscountCode | None, Decimal]:
    """
    پیدا کردن و اعمال کد تخفیف (در صورت وجود).
    """
    if not discount_code:
        return None, Decimal("0")

    discount_obj = (
        DiscountCode.objects
        .select_for_update()
        .filter(code__iexact=discount_code)
        .first()
    )
    if not discount_obj:
        raise ValidationError({"detail": "کد تخفیف معتبر نیست"})

    items = list(order.items.select_related("course"))

    # اگر کد تخفیف روی دوره مشخصی ست شده
    target_course = None
    if discount_obj.course:
        for item in items:
            if item.course_id == discount_obj.course_id:
                target_course = item.course
                break
        if not target_course:
            raise ValidationError({"detail": "کد تخفیف برای این دوره معتبر نیست"})
    else:
        target_course = None  # کد عمومی

    # استفاده از can_use برای همه چک‌ها
    if not discount_obj.can_use(order.user, target_course):
        raise ValidationError({"detail": "کد تخفیف معتبر نیست یا شرایط استفاده را ندارد"})

    # محاسبه مبلغ تخفیف
    if discount_obj.discount_type == "percent":
        discount_amount = subtotal * discount_obj.value / Decimal("100")
    else:  # fixed
        discount_amount = discount_obj.value

    # حداکثر تخفیف = subtotal
    if discount_amount > subtotal:
        discount_amount = subtotal

    # افزایش شمارنده استفاده
    discount_obj.increment_usage()

    return discount_obj, discount_amount


def finalize_order(
    order: Order,
    subtotal: Decimal,
    discount_obj: DiscountCode | None,
    discount_amount: Decimal,
) -> Decimal:
    """
    قرار دادن مقادیر نهایی روی سفارش و تغییر وضعیت به paid.
    """
    total = subtotal - discount_amount
    if total < 0:
        total = Decimal("0")

    order.total_amount = total
    order.status = "paid"
    order.discount_code = discount_obj.code if discount_obj else None
    order.save()

    return total


def create_payment(order: Order, total: Decimal) -> Payment:
    """
    ثبت رکورد پرداخت؛ فعلاً فرض می‌کنیم پرداخت موفق است.
    """
    payment = Payment.objects.create(
        order=order,
        amount=total,
        status="paid",
        # payment_date auto_now_add است
    )
    return payment


def create_enrollments(order: Order) -> None:
    """
    برای هر participant در هر آیتم، یک Enrollment می‌سازد.
    """
    items = order.items.prefetch_related("participants", "course")

    for item in items:
        for participant in item.participants.all():
            Enrollment.objects.get_or_create(
                user=order.user,
                course=item.course,
                participant=participant,
            )
