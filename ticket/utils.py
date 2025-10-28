from django.core.mail import send_mail
from django.conf import settings


# ایمیل اطلاع‌رسانی
def send_ticket_reply_email(user, ticket, reply):
    subject = f"پاسخ جدید برای تیکت شما: {ticket.title}"
    message = f"سلام {user.get_full_name()},\n\nتیکت شما پاسخ داده شد:\n\n{reply.message}\n\nبرای مشاهده کامل، وارد پنل خود شوید."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

# پیامک اطلاع‌رسانی
def send_ticket_reply_sms(user, ticket, reply):
    sms_text = f"تیکت شما پاسخ داده شد: {ticket.title}\n{reply.message[:50]}."
    # TODO: send_sms
    # send_sms(user.mobile, message)
