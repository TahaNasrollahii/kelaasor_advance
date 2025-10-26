from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from courses.models import Course


@shared_task
def increase_online_course_price_before_deadline():
    """
    افزایش قیمت دوره آنلاین به میزان 10% اگر کمتر از 5 روز به پایان ثبت نام مانده باشد
    """
    now = timezone.now()
    threshold = now + timedelta(days=5)

    courses = Course.objects.filter(
        course_type="online",
        registration_deadline__lte=threshold,
        registration_deadline__gte=now,
        is_active=True,
    )

    for course in courses:
        original_price = course.price
        course.price = round(course.price * 1.10, 2)  # افزایش 10%
        course.save()
        print(f"Course '{course.title}' price increased from {original_price} to {course.price}")
