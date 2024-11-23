from celery import shared_task

from .fcm import send_notification_to_multiple_user


@shared_task(bind=True)
def celery_send_fcm_notification(
    self,
    tokens: list,
    title: None,
    body: None,
    data: dict | None,
):
    """Send the notifications to given device ids

    Args:
        device_ids (list): list of device registration tokens
        title (None): title
        body (None): body
        data (dict): extra data (Optional)
    """
    send_notification_to_multiple_user(title, body, tokens=tokens)
