from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from realstate_new.api.notification.notification_service import celery_send_fcm_notification
from realstate_new.application.models import JobApplication
from realstate_new.users.models import FCMDevice
from realstate_new.utils.base_models import TrackingModel

from .choices import BrokerageType
from .choices import JobType
from .choices import LockBoxType


class BaseTask(TrackingModel):
    title = models.CharField(max_length=50, default="")
    property = models.ForeignKey(
        "master.Property",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    client_name = models.CharField(max_length=50, default="", blank=True)
    client_phone = models.CharField(max_length=50, default="", blank=True)
    client_email = models.EmailField(blank=True)

    task_time = models.DateTimeField()
    asap = models.BooleanField(_("As Soon As Possible"), null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    payment_amount = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    job_type = models.CharField(
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
    vacant = models.BooleanField(default=False)
    pets = models.BooleanField(default=False)
    concierge = models.BooleanField(default=False)

    alarm_code = models.CharField(max_length=50, default="", blank=True)
    gate_code = models.CharField(max_length=50, default="", blank=True)

    lockbox_type = models.CharField(
        max_length=50,
        choices=LockBoxType.choices,
        default=LockBoxType.OTHER,
        blank=True,
    )

    applications = GenericRelation(
        JobApplication,
        content_type_field="content_type",
        object_id_field="task_id",
    )
    not_acceptance_notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client_name}-{self.payment_amount}"

    class Meta:
        abstract = True

    def process_payment_after_approve(
        self,
        amount,
    ):
        """This function initiates the payment after the task creater has approved the task submission."""  # noqa: E501
        # TODO:
        # Trigger after the task is approved by the creater.

    def save(self, *args, **kwargs) -> None:
        try:
            old_instance = self.__class__.objects.get(id=self.id)
        except Exception:  # noqa: BLE001
            old_instance = None
        if old_instance and not old_instance.assigned_to and self.assigned_to:
            device = FCMDevice.objects.get(user=self.created_by)
            body = f"Great news! {self.assigned_to.get_full_name}\
                     has accepted your job {self.title}."
            celery_send_fcm_notification.delay(
                title=f"Your task has been accepted by {self.assigned_to.username}",
                device_ids=[device.registration_id],
                body=body,
                data={},
            )
        return super().save(*args, **kwargs)
