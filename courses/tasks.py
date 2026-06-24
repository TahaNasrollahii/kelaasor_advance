import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from courses.defaults import COURSE_PRICE_INCREASE_DAYS, COURSE_PRICE_INCREASE_PERCENTAGE
from courses.models import Course

logger = logging.getLogger(__name__)


@shared_task
def increase_online_course_price_before_deadline():
    """
    Increase online course prices by a configured percentage when the
    registration deadline is within COURSE_PRICE_INCREASE_DAYS.
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
        original_price = course.price
        increase_percentage = COURSE_PRICE_INCREASE_PERCENTAGE / 100
        course.price = round(course.price * (1 + increase_percentage), 2)
        course.save()
        logger.info("Course '%s' price increased from %s to %s", course.title, original_price, course.price)
