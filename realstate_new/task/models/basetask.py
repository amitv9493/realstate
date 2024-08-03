from django.contrib.auth import get_user_model
from django.db import models

from realstate_new.utils.base_models import TrackingModel

from .types import BrokerageType
from .types import JobType


class BaseTask(TrackingModel):
    property = models.ForeignKey(
        "master.Property",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    client_name = models.CharField(max_length=50)
    client_phone = models.CharField(max_length=50)
    client_email = models.EmailField()
    task_time = models.DateTimeField()
    notes = models.TextField()
    payment_amount = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    job_type = models.CharField(
        max_length=5,
        choices=JobType.choices,
        default=JobType.apply,
    )
    job_deadline = models.DateTimeField()
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

    show_client_phone_number = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client_name}-{self.payment_amount}"

    class Meta:
        abstract = True
