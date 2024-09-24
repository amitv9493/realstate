from django.db import models

from .basetask import BaseTask
from .choices import RunnerTaskType


class RunnerTask(BaseTask):
    task_type = models.CharField(max_length=50, choices=RunnerTaskType.choices)
    instructions = models.TextField()
    closing_location_address = models.TextField()

    # in case of paperwork type runner task
    pickup_address = models.TextField()
    dropoff_address = models.TextField()

    # MEET DELIVERY OR VENDOR ONLY
    vendor_name = models.CharField(max_length=50)
    vendor_phone = models.CharField(max_length=50)
    vendor_company_name = models.CharField(max_length=50)
    vebdor_notes = models.TextField()

    @property
    def type_of_task(self):
        return "Runner"
