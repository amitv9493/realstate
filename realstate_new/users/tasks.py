from celery import shared_task
from firebase_admin import messaging

from .models import User


@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@shared_task(bind=True)
def send_fcm_notification(
    self,
    device_ids: list,
    title: None,
    body: None,
    data: dict,
):
    messages = []
    for i in device_ids:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=i,
        )
        messages.append(message)
        messaging.send_each(messages)
