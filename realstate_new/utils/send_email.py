from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task()
def send_email(
    recipient_list: list[str],
    subject: str,
    body: str | None = None,
    context: dict | None = None,
    template_path: str | None = None,
):
    from_email = settings.EMAIL_HOST_USER

    if template_path:
        html_message = render_to_string(template_path, context=context or {})
        plain_message = strip_tags(html_message)
    else:
        html_message = None
        plain_message = body

    message = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=from_email,
        to=recipient_list,
    )

    if html_message:
        message.attach_alternative(html_message, "text/html")

    return message.send()
