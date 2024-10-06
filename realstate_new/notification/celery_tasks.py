from celery import shared_task
from firebase_admin import messaging

from .templates import NotificationMetaData


@shared_task(bind=True)
def celery_send_fcm_notification(
    self,
    device_ids: list,
    title: None,
    body: None,
    data: dict,
):
    """Send the notifications to given device ids

    Args:
        device_ids (list): list of device registration tokens
        title (None): title
        body (None): body
        data (dict): extra data (Optional)
    """
    send_bulk_notification(
        device_ids,
        title,
        body,
        data,
    )


def send_bulk_notification(
    device_ids: list,
    title: None,
    body: None,
    data: dict,
):
    """Send the notifications to given device ids

    Args:
        device_ids (list): list of device registration tokens
        title (None): title
        body (None): body
        data (dict): extra data (Optional)
    """
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


@shared_task
def celery_send_individual_notification(data_list: list[NotificationMetaData]):
    send_individual_notification(data_list=data_list)


def send_individual_notification(data_list: list[NotificationMetaData]):
    messages = []
    for data in data_list:
        message = messaging.Message(
            notification=messaging.Notification(
                title=data.title,
                body=data.body,
            ),
            data=data.data,
            token=data.device_id,
        )
        messages.append(message)
    messaging.send_each(messages)
