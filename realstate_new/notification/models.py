import logging

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from realstate_new.task.models.choices import TaskStatusChoices
from realstate_new.utils import send_email

from .celery_tasks import celery_send_fcm_notification
from .templates import get_notification_template

_logger = logging.getLogger(__name__)


class NotificationManager(models.Manager):
    def create_notifications(self, task, event, users: list, **kwargs):
        for user in users:
            if user:
                self.create(event=event, user=user, content_object=task, **kwargs)
        return True


class NotificationChoices(models.TextChoices):
    DETAILS_UPDATED = "DETAILS_UPDATED", "Details Updated"
    REMINDER_24 = "REMINDER_24", "24 Hour Reminder"
    REMINDER_1 = "REMINDER_1", "1 Hour Reminder"
    JOB_NOT_ACCEPTED_YET = "JOB_NOT_ACCEPTED_YET", "JOB_NOT_ACCEPTED_YET"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    event = models.CharField(
        max_length=20,
        choices=NotificationChoices.choices + TaskStatusChoices.choices,
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    description = models.TextField(blank=True, default="")
    extra_data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
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
            self.handle_task_objects(ctx_obj=ctx_obj)
            self.is_sent = True
        super().save(*args, **kwargs)

    def handle_task_objects(self, ctx_obj):
        task_time = timezone.localtime(ctx_obj.task_time).strftime("%I:%M %p")
        time = timezone.localtime(timezone.now()).strftime("%I:%M %p")

        n_title, n_body, n_body2 = get_notification_template(
            event_type=self.event,
            type_of_task=ctx_obj.type_of_task,
            agent_name=(ctx_obj.assigned_to.get_full_name() if ctx_obj.assigned_to else None),
            now=time,
            task_time=task_time,
        )
        # Check if the notification is for job creater.
        if self.user == ctx_obj.created_by and not self.is_sent:
            notification_body = n_body
            device_ids = list(
                ctx_obj.created_by.fcmdevices.all().values_list(
                    "registration_id",
                    flat=True,
                ),
            )
            log_msg = f"task:{self.object_id} type:created_by deviceIds{device_ids}"
            _logger.info(log_msg)
            email_reciver = [self.user.email]

        # Check if the notification is for job assigner.
        if self.user == ctx_obj.assigned_to and not self.is_sent:
            notification_body = n_body2
            device_ids = list(
                ctx_obj.assigned_to.fcmdevices.all().values_list(
                    "registration_id",
                    flat=True,
                ),
            )
            log_msg = f"task:{self.object_id} type:assigned_to deviceIds{device_ids}"
            _logger.info(log_msg)

            email_reciver = [self.user.email]

        self.description = notification_body

        celery_send_fcm_notification.delay(
            title=n_title,
            body=notification_body,
            tokens=device_ids,
        )

        if self.event in TaskStatusChoices._member_names_:
            self.content_object.status = self.event
            self.content_object.save(update_fields=["status"])

        send_email.delay(
            recipient_list=email_reciver,
            subject=n_title,
            body=notification_body,
            context={
                "title": n_title,
                "body": notification_body,
            },
            template_path="emails/base.html",
        )
