import contextlib

import firebase_admin
from django.conf import settings
from django.http import JsonResponse
from firebase_admin import credentials
from firebase_admin import messaging


def initialize_firebase():
    if not firebase_admin._apps:  # noqa: SLF001
        cred = credentials.Certificate(settings.FIREBASE_ADMIN_CREDENTIALS)
        firebase_admin.initialize_app(cred)


def send_push_notification(token, title, body, data=None):
    initialize_firebase()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data=data or {},
    )

    try:
        response = messaging.send(message)
    except Exception as e:  # noqa: BLE001
        return f"Error sending message: {e!s}"
    else:
        return f"Successfully sent message: {response}"


def send_topic_notification(topic, title, body, data=None):
    initialize_firebase()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic=topic,
        data=data or {},
    )

    with contextlib.suppress(Exception):
        messaging.send(message)


def fcm(request):
    send_topic_notification("topic-1", "notification 1", "notification ")
    return JsonResponse({1: 1})
