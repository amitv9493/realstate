from django.db import models

from .basetask import BaseTask
from .choices import RunnerTaskType


class RunnerTask(BaseTask):
    property_address = models.OneToOneField(
        "master.Property",
        on_delete=models.CASCADE,
        null=True,
    )
    task_type = models.CharField(max_length=50, choices=RunnerTaskType.choices)

    # in case of paperwork type runner task (This is still optional)
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

    # Need to discuss
    # MEET DELIVERY OR VENDOR ONLY
    vendor_name = models.CharField(max_length=50, blank=True, default="")
    vendor_phone = models.CharField(max_length=50, blank=True, default="")
    vendor_company_name = models.CharField(max_length=50, blank=True, default="")
    vendor_notes = models.TextField(blank=True, default="")

    @property
    def type_of_task(self):
        return "Runner"
