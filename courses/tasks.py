from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from courses.defaults import COURSE_PRICE_INCREASE_DAYS, COURSE_PRICE_INCREASE_PERCENTAGE
from courses.models import Course


@shared_task
def increase_online_course_price_before_deadline():
    """
    افزایش قیمت دوره آنلاین به میزان درصدی که در تنظیمات مشخص شده است،
    اگر کمتر از مقدار مشخصی (معمولاً ۵ روز) به پایان مهلت ثبت‌نام باقی‌مانده باشد.

    این تابع به‌طور خودکار برای دوره‌های آنلاین که تاریخ پایان ثبت‌نام آنها
    در بازه زمانی مشخص شده (کمتر از `COURSE_PRICE_INCREASE_DAYS` روز باقی مانده باشد)
    اجرا می‌شود و قیمت آنها را بر اساس درصد افزایش داده شده در تنظیمات تغییر می‌دهد.
    """

    now = timezone.now()
    threshold = now + timedelta(days=COURSE_PRICE_INCREASE_DAYS)

    courses = Course.objects.filter(
        course_type="online",
        registration_deadline__lte=threshold,
        registration_deadline__gte=now,
        is_active=True,
    )

    for course in courses:
        original_price = course.price  # قیمت اصلی دوره
        increase_percentage = COURSE_PRICE_INCREASE_PERCENTAGE / 100  # تبدیل درصد به عدد اعشاری
        course.price = round(course.price * (1 + increase_percentage), 2)  # افزایش قیمت و گرد کردن به دو رقم اعشار
        course.save()  # ذخیره قیمت جدید
        print(f"Course '{course.title}' price increased from {original_price} to {course.price}")
