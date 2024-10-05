from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from realstate_new.api.notification.notification_service import NotificationTemplates
from realstate_new.api.notification.notification_service import celery_send_fcm_notification
from realstate_new.users.models import FCMDevice

from .choices import EventChoices


class TaskHistory(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    event = models.CharField(max_length=20, choices=EventChoices.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    description = models.TextField(blank=True, default="")
    extra_data = models.JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.get_event_display()} - {self.content_object} at {self.timestamp}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        template = getattr(NotificationTemplates, self.event, None)
        device_ids = list(
            set(
                FCMDevice.objects.filter(
                    user=self.content_object.created_by,
                ).values_list("registration_id", flat=True),
            ),
        )
        if template and device_ids:
            celery_send_fcm_notification.delay(
                title=template.title,
                body=template.body,
                data={},
                device_ids=device_ids,
            )
