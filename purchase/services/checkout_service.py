import logging
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

logger = logging.getLogger('purchase')


def get_pending_order(user: "User") -> Order:
    """Return the user's pending order with a row lock for atomic operations."""
    order = (
        Order.objects
        .select_for_update()
        .filter(user=user, status="pending")
        .first()
    )
    if not order:
        logger.warning("Checkout attempted with empty cart for user %s", user.pk)
        raise ValidationError({"detail": "Your cart is empty"})

    if not order.items.exists():
        logger.warning("Checkout attempted with empty order items for user %s, order %s", user.pk, order.pk)
        raise ValidationError({"detail": "No items found in your cart"})

    return order


def attach_participants_to_order(order: Order, items_payload: list[dict]) -> None:
    """
    Attach participants to the corresponding OrderItems and update quantity.
    items_payload structure:
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
    Validated beforehand by CheckoutSerializer.
    """
    order_items = list(order.items.select_related("course"))

    participants_by_course = {
        item["course_id"]: item["participants"]
        for item in items_payload
    }

    # Course in cart but missing from payload
    for order_item in order_items:
        if order_item.course_id not in participants_by_course:
            raise ValidationError({
                "detail": f"No participants provided for course {order_item.course_id}"
            })

    # Course in payload but not in cart
    course_ids_in_cart = {item.course_id for item in order_items}
    for course_id in participants_by_course.keys():
        if course_id not in course_ids_in_cart:
            raise ValidationError({
                "detail": f"Course {course_id} is not in your cart"
            })

    # Create/update participants and quantity
    for order_item in order_items:
        participants_data = participants_by_course[order_item.course_id]

        order_item.participants.all().delete()

        for p in participants_data:
            Participant.objects.create(
                order_item=order_item,
                full_name=p["full_name"],
                email=p.get("email"),
                mobile=p.get("mobile"),
            )

        order_item.quantity = len(participants_data)
        order_item.save()


def calculate_subtotal(order: Order) -> Decimal:
    """Calculate the subtotal before discount (price * quantity for each item)."""
    items = order.items.all()
    subtotal = sum((item.price * item.quantity for item in items), Decimal("0"))
    return subtotal


def apply_discount(
    order: Order,
    subtotal: Decimal,
    discount_code: str | None,
) -> tuple[DiscountCode | None, Decimal]:
    """Find and apply a discount code if provided."""
    if not discount_code:
        return None, Decimal("0")

    discount_obj = (
        DiscountCode.objects
        .select_for_update()
        .filter(code__iexact=discount_code)
        .first()
    )
    if not discount_obj:
        raise ValidationError({"detail": "Invalid discount code"})

    items = list(order.items.select_related("course"))

    target_course = None
    if discount_obj.course:
        for item in items:
            if item.course_id == discount_obj.course_id:
                target_course = item.course
                break
        if not target_course:
            raise ValidationError({"detail": "Discount code is not valid for this course"})
    else:
        target_course = None

    if not discount_obj.can_use(order.user, target_course):
        raise ValidationError({"detail": "Discount code is invalid or does not meet usage conditions"})

    if discount_obj.discount_type == "percent":
        discount_amount = subtotal * discount_obj.value / Decimal("100")
    else:
        discount_amount = discount_obj.value

    if discount_amount > subtotal:
        discount_amount = subtotal

    discount_obj.increment_usage()

    return discount_obj, discount_amount


def finalize_order(
    order: Order,
    subtotal: Decimal,
    discount_obj: DiscountCode | None,
    discount_amount: Decimal,
) -> Decimal:
    """Set final values on the order and change status to paid."""
    total = subtotal - discount_amount
    if total < 0:
        total = Decimal("0")

    order.total_amount = total
    order.status = "paid"
    order.discount_code = discount_obj.code if discount_obj else None
    order.save()
    logger.info("Order %s finalized: subtotal=%s, discount=%s, total=%s", order.pk, subtotal, discount_amount, total)

    return total


def create_payment(order: Order, total: Decimal) -> Payment:
    """Create a payment record. Currently assumes payment succeeds."""
    payment = Payment.objects.create(
        order=order,
        amount=total,
        status="paid",
    )
    logger.info("Payment created for order %s: amount=%s", order.pk, total)
    return payment


def create_enrollments(order: Order) -> None:
    """Create an Enrollment for each participant in each order item."""
    items = order.items.prefetch_related("participants", "course")
    enrollment_count = 0

    for item in items:
        for participant in item.participants.all():
            _, created = Enrollment.objects.get_or_create(
                user=order.user,
                course=item.course,
                participant=participant,
            )
            if created:
                enrollment_count += 1

    logger.info("Created %d enrollments for order %s", enrollment_count, order.pk)
