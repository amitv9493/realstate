from django.db import models

from .basetask import BaseTask
from .choices import RunnerTaskType


class RunnerTask(BaseTask):
    task_type = models.CharField(max_length=50, choices=RunnerTaskType.choices)
    instructions = models.TextField(blank=True, default="")

    # in case of paperwork type runner task
    pickup_address = models.OneToOneField(
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

    # MEET DELIVERY OR VENDOR ONLY
    vendor_name = models.CharField(max_length=50, blank=True, default="")
    vendor_phone = models.CharField(max_length=50, blank=True, default="")
    vendor_company_name = models.CharField(max_length=50, blank=True, default="")
    vendor_notes = models.TextField(blank=True, default="")

    @property
    def type_of_task(self):
        return "Runner"
