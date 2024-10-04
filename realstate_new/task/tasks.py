from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from realstate_new.api.notification import NotificationMetaData
from realstate_new.api.notification import NotificationTemplates
from realstate_new.api.notification import send_individual_notification
from realstate_new.master.models.types import JOB_TYPE_MAPPINGS


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
