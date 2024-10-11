from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import now

from realstate_new.master.models.types import JOB_TYPE_MAPPINGS
from realstate_new.notification.models import Notification
from realstate_new.notification.models import NotificationChoices

logger = get_task_logger(__name__)


@shared_task(bind=True)
def check_task_expiry(self):
    """This function checks if a task is reaching its deadline to
    24 hours before the task time. It does not process the ASAP jobs.
    """
    filtered_qs = []
    for job_models in JOB_TYPE_MAPPINGS.values():
        qs = job_models.objects.filter(
            asap=False,
            not_acceptance_notification_sent=False,
            is_cancelled=False,
            marked_completed_by_assignee=False,
            assigned_to__isnull=True,
            task_time__gte=now(),
            task_time__lte=now() + timedelta(hours=24),
        )
        filtered_qs.extend(list(qs))
    logger.info(filtered_qs)
    for task in filtered_qs:
        Notification.objects.create_notifications(
            task=task,
            event=NotificationChoices.JOB_NOT_ACCEPTED_YET,
            users=[task.created_by],
        )
        task.not_acceptance_notification_sent = True
        task.save(update_fields=["not_acceptance_notification_sent"])

    msg = "Successfully processed %d tasks." % (len(filtered_qs))
    logger.info(msg)
    return msg


@shared_task(bind=True)
def job_reminder(self, reminder_time):
    event = (
        NotificationChoices.REMINDER_24
        if reminder_time == timedelta(hours=24).total_seconds()
        else NotificationChoices.REMINDER_1
    )
    filtered_qs = []
    for job_models in JOB_TYPE_MAPPINGS.values():
        qs = (
            job_models.objects.filter(
                asap=False,
                is_cancelled=False,
                assigned_to__isnull=False,
                task_time__gte=now(),
                task_time__lte=now() + timedelta(seconds=reminder_time),
            )
            .exclude(notifications__event=event)
            .distinct()
        )
        filtered_qs.extend(list(qs))
    count = 0
    for i in filtered_qs:
        Notification.objects.create_notifications(
            task=i,
            event=event,
            users=[i.created_by, i.assigned_to],
        )
        count += 1
    msg = "Successfully processed %d tasks." % count
    logger.info(msg)
    return msg
