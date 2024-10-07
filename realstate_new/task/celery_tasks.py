from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import now

from realstate_new.master.models.types import JOB_TYPE_MAPPINGS
from realstate_new.notification.celery_tasks import send_individual_notification
from realstate_new.notification.models import EventChoices
from realstate_new.notification.models import Notification
from realstate_new.notification.templates import NotificationMetaData
from realstate_new.notification.templates import NotificationTemplates

logger = get_task_logger(__name__)


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
            is_cancelled=False,
            assigned_to__isnull=True,
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
    msg = "Successfully processed %d tasks." % (len(messages))
    logger.info(msg)
    return msg


@shared_task(bind=True)
def job_reminder(self, reminder_time):
    filtered_qs = []
    for job_models in JOB_TYPE_MAPPINGS.values():
        qs = (
            job_models.objects.filter(
                asap=False,
                is_cancelled=False,
                assigned_to__isnull=False,
                task_time__lte=now() + timedelta(seconds=reminder_time),
            )
            .exclude(notifications__event=EventChoices.REMINDER_24)
            .distinct()
        )
        filtered_qs.extend(list(qs))
        count = 0
        for i in filtered_qs:
            Notification.objects.create_notifications(
                task=i,
                event=EventChoices.REMINDER_24,
                users=[i.created_by, i.assigned_to],
            )
            count += 1
    msg = "Successfully processed %d tasks." % count
    logger.info(msg)
    return msg
