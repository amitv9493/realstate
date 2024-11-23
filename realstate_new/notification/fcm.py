import json
import logging
from typing import TypedDict

import google.auth.transport.requests
import requests
from django.conf import settings
from firebase_admin.credentials import service_account
from rest_framework import status

_logger = logging.getLogger(__name__)


class Message(TypedDict):
    title: str
    body: str
    token: str


class FCM:
    PROJECT_ID = settings.FIREBASE_PROJECT_ID
    BASE_URL = "https://fcm.googleapis.com"
    FCM_ENDPOINT = "v1/projects/" + PROJECT_ID + "/messages:send"
    FCM_URL = BASE_URL + "/" + FCM_ENDPOINT
    SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

    def _get_access_token(self):
        credentials = service_account.Credentials.from_service_account_file(
            settings.FIREBASE_ADMIN_CERT,
            scopes=self.SCOPES,
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    def send_fcm_message(self, fcm_message):
        """Send HTTP request to FCM with given message.

        Args:
        fcm_message: JSON object that will make up the body of the request.
        """
        headers = {
            "Authorization": "Bearer " + self._get_access_token(),
            "Content-Type": "application/json; UTF-8",
        }
        resp = requests.post(
            self.FCM_URL,
            data=json.dumps(fcm_message),
            headers=headers,
            timeout=20,
        )

        if resp.status_code == status.HTTP_200_OK:
            _logger.info("Message sent to Firebase for delivery")

        elif resp.status_code == status.HTTP_404_NOT_FOUND:
            _logger.info("FCM device is stale")

        else:
            msg = f"Unable to send message to Firebase {resp.status_code} {resp.text}"
            _logger.critical(msg)

    def build_common_message(self, title, body, token):
        """Construct common notifiation message.

        Construct a JSON object that will be used to define the
        common parts of a notification message that will be sent
        to any app instance subscribed to the news topic.
        """
        return {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body,
                },
            },
        }

    def build_override_message(self):
        """Construct common notification message with overrides.

        Constructs a JSON object that will be used to customize
        the messages that are sent to iOS and Android devices.
        """
        fcm_message = self.build_common_message()

        apns_override = {
            "payload": {"aps": {"badge": 1}},
            "headers": {"apns-priority": "10"},
        }

        android_override = {
            "notification": {"click_action": "android.intent.action.MAIN"},
        }

        fcm_message["message"]["android"] = android_override
        fcm_message["message"]["apns"] = apns_override

        return fcm_message


def send_individual_notification(title, body, token):
    """Send a single notification."""
    fcm = FCM()
    message = fcm.build_common_message(title, body, token)
    fcm.send_fcm_message(message)


def send_notification_to_multiple_user(title: str, body: str, tokens: list):
    """Send same notification to multiple user."""
    fcm = FCM()
    for token in tokens:
        message = fcm.build_common_message(title, body, token)
        fcm.send_fcm_message(message)


def send_batch_notification(messages: list[Message]):
    """Send different notification to different user."""
    fcm = FCM()
    for message in messages:
        msg = fcm.build_common_message(
            title=message["title"],
            body=message["body"],
            token=message["token"],
        )
        fcm.send_fcm_message(msg)
