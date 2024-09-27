from django.db import models

from .basetask import BaseTask
from .choices import LockBoxType
from .choices import SignTaskType


class SignTask(BaseTask):
    task_type = models.CharField(max_length=50, choices=SignTaskType.choices)
    sign_type = models.CharField(max_length=50, blank=True, default="")
    instructions = models.TextField(blank=True, default="")

    install_address = models.OneToOneField(
        "master.Property",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    pickup_address = models.OneToOneField(
        "master.Property",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    remove_address = models.OneToOneField(
        "master.Property",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    dropoff_address = models.OneToOneField(
        "master.Property",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    lockbox_type = models.CharField(
        max_length=50,
        choices=LockBoxType.choices,
        blank=True,
    )

    @property
    def type_of_task(self):
        return "Sign"
