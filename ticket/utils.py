from django.core.mail import send_mail
from django.conf import settings


def send_ticket_reply_email(user, ticket, reply):
    """Send email notification when a ticket receives a reply."""
    subject = f"New reply for your ticket: {ticket.title}"
    message = f"Hello {user.get_full_name()},\n\nYour ticket has been replied to:\n\n{reply.message}\n\nPlease log in to view the full conversation."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_ticket_reply_sms(user, ticket, reply):
    """Send SMS notification when a ticket receives a reply. Currently stubbed."""
    sms_text = f"Your ticket has been replied to: {ticket.title}\n{reply.message[:50]}."
    # TODO: Integrate with SMS provider
    # send_sms(user.mobile, sms_text)
