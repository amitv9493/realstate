from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from realstate_new.application.models import JobApplication
from realstate_new.notification.models import Notification
from realstate_new.utils.base_models import TrackingModel

from .choices import BrokerageType
from .choices import JobType
from .choices import TaskStatusChoices


class BaseTask(TrackingModel):
    client_name = models.CharField(max_length=50, default="", blank=True)
    client_phone = ArrayField(
        base_field=models.CharField(max_length=50),
        null=True,
        blank=True,
    )
    client_email = ArrayField(base_field=models.EmailField(), null=True, blank=True)

    task_time = models.DateTimeField()
    asap = models.BooleanField(_("As Soon As Possible"), default=False)
    notes = models.TextField(blank=True, default="")

    payment_amount = models.PositiveIntegerField()
    is_verified = models.BooleanField(default=False)
    application_type = models.CharField(
        max_length=5,
        choices=JobType.choices,
        default=JobType.apply,
    )
    apply_deadline = models.DateTimeField(null=True, blank=True)

    assigned_to = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_assigned",
    )
    brokerage = models.CharField(
        max_length=50,
        choices=BrokerageType.choices,
        default=BrokerageType.my_brokerage,
    )

    show_client_info = models.BooleanField(default=False)

    # extra info

    not_acceptance_notification_sent = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    marked_completed_by_assignee = models.BooleanField(default=False)
    audio_file = models.FileField(
        upload_to="additional-audio-notes/",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        default=TaskStatusChoices.CREATED,
        choices=TaskStatusChoices.choices,
    )
    # GenericRelations
    notifications = GenericRelation(Notification)
    applications = GenericRelation(
        JobApplication,
        content_type_field="content_type",
        object_id_field="task_id",
    )

    def __str__(self):
        return f"{self.client_name}-{self.payment_amount}"

    class Meta:
        abstract = True
