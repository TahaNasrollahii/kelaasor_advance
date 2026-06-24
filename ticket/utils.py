from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.translation import (
    EMAIL_TICKET_REPLY_SUBJECT,
    EMAIL_TICKET_REPLY_BODY,
    SMS_TICKET_REPLY,
)


def send_ticket_reply_email(user, ticket, reply):
    """Send email notification when a ticket receives a reply."""
    subject = EMAIL_TICKET_REPLY_SUBJECT.format(title=ticket.title)
    message = EMAIL_TICKET_REPLY_BODY.format(
        name=user.get_full_name(),
        message=reply.message
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_ticket_reply_sms(user, ticket, reply):
    """Send SMS notification when a ticket receives a reply. Currently stubbed."""
    sms_text = SMS_TICKET_REPLY.format(
        title=ticket.title,
        message=reply.message[:50]
    )
    # TODO: Integrate with SMS provider
    # send_sms(user.mobile, sms_text)
