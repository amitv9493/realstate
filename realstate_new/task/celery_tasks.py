import json
from datetime import timedelta
from typing import TypedDict

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django_redis import get_redis_connection

from realstate_new.api.notification import NotificationMetaData
from realstate_new.api.notification import NotificationTemplates
from realstate_new.api.notification import send_individual_notification
from realstate_new.master.models.types import JOB_TYPE_MAPPINGS

from .models import TaskHistory

redis_conn = get_redis_connection("default")

logger = get_task_logger(__name__)


class EventMessage(TypedDict):
    event_type: str
    model: str
    content_id: int
    description: str | None
    extra_data: dict | None


@shared_task(bind=True)
def check_task_expiry(self):
    """This function checks if a task is reaching its deadline to
    24 hours before the task time. It does not process the ASAP jobs.
    """
    template = NotificationTemplates.JOB_NOT_ACCEPTED_YET

    filtered_qs = []
    for job_models in JOB_TYPE_MAPPINGS.values():
        qs = job_models.objects.filter(
            asap=False,
            not_acceptance_notification_sent=False,
            task_time__lte=now() + timedelta(hours=24),
        )
        filtered_qs.append(qs)

    messages = []
    for qs in filtered_qs:
        device_ids = qs.values(
            "created_by__fcmdevices__registration_id",
            "title",
        )
        messages.extend(
            NotificationMetaData(
                data={},
                title=template.title,
                body=template.body.format(job_title=device_id["title"]),
                device_id=device_id["created_by__fcmdevices__registration_id"],
            )
            for device_id in device_ids
        )
    if messages:
        send_individual_notification(data_list=messages)
        for _qs in filtered_qs:
            _qs.update(not_acceptance_notification_sent=True)
    return "Successfully processed %d tasks." % (len(messages))


@shared_task(bind=True)
def process_task_events(self, queue_name, batch_size=100):
    events = 0
    for _ in range(batch_size):
        message = redis_conn.lpop(queue_name)

        if message:
            decode_msg = message.decode("utf-8")
            msg = json.loads(decode_msg)
            model = JOB_TYPE_MAPPINGS[msg["model"]]
            content_object = model.objects.get(id=int(msg["content_id"]))
            desc = None
            if user_id := msg.get("extra_data", {}).get("cancelled_by", None):
                assigned_user = get_user_model().objects.get(id=user_id)
                desc = f"Task was cancelled by user {assigned_user.get_username()}"

            TaskHistory.objects.create(
                event=msg["event_type"],
                content_object=content_object,
                description=desc if desc else "",
            )
            events += 1

    logger.info("Successfully processed %d task events.", events)
