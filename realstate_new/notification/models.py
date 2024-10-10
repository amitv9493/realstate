from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from .celery_tasks import celery_send_fcm_notification
from .templates import get_notification_template


class NotificationManager(models.Manager):
    def create_notifications(self, task, event, users: list, **kwargs):
        for user in users:
            self.create(event=event, user=user, content_object=task, **kwargs)
        return True


class EventChoices(models.TextChoices):
    CREATED = "CREATED", "Task Created"
    ASSIGNED = "ASSIGNED", "Task Assigned"
    STARTED = "STARTED", "Task Started"
    VERIFIED = "VERIFIED", "Task Verified"
    CREATER_CANCELLED = "CREATER_CANCELLED", "Task Cancelled by creater"
    ASSIGNER_CANCELLED = "ASSIGNER_CANCELLED", "Task Cancelled by assigner"
    REASSIGNED = "REASSIGNED", "Task Reassigned"
    DETAILS_UPDATED = "DETAILS_UPDATED", "Details Updated"
    REMINDER_24 = "REMINDER_24", "24 Hour Reminder"
    REMINDER_1 = "REMINDER_1", "1 Hour Reminder"
    MARK_COMPLETED = "MARK_COMPLETED", "Task Marked Completed"
    JOB_NOT_ACCEPTED_YET = "JOB_NOT_ACCEPTED_YET", "JOB_NOT_ACCEPTED_YET"


class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    event = models.CharField(max_length=20, choices=EventChoices.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    description = models.TextField(blank=True, default="")
    extra_data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)

    objects = NotificationManager()

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.get_event_display()} - {self.content_object} at {self.timestamp}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            ctx_obj = self.content_object

            task_time = timezone.localtime(ctx_obj.task_time).strftime("%I:%M %p")
            time = timezone.localtime(timezone.now()).strftime("%I:%M %p")

            n_title, n_body, n_body2 = get_notification_template(
                event_type=self.event,
                job_title=ctx_obj.title,
                agent_name=(ctx_obj.assigned_to.get_full_name() if ctx_obj.assigned_to else None),
                now=time,
                task_time=task_time,
            )
            # Check if the notification is for job creater.
            if self.user == ctx_obj.created_by:
                notification_body = n_body
                device_ids = list(
                    ctx_obj.created_by.fcmdevices.all().values_list(
                        "registration_id",
                        flat=True,
                    ),
                )
            # Check if the notification is for job assigner.
            if self.user == ctx_obj.assigned_to:
                notification_body = n_body2

                device_ids = list(
                    ctx_obj.assigned_to.fcmdevices.all().values_list(
                        "registration_id",
                        flat=True,
                    ),
                )
            self.description = notification_body

            celery_send_fcm_notification.delay(
                title=n_title,
                body=notification_body,
                data={},
                device_ids=device_ids,
            )
        super().save(*args, **kwargs)
