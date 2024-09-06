from django.db import models

from .basetask import BaseTask
from .choices import LockBoxType
from .choices import SignTaskType


class SignTask(BaseTask):
    task_type = models.CharField(max_length=50, choices=SignTaskType.choices)
    sign_type = models.CharField(max_length=50)
    instructions = models.TextField()

    collection_address = models.TextField()
    dropoff_address = models.TextField()
    lockbox_type = models.CharField(
        max_length=50,
        choices=LockBoxType.choices,
        blank=True,
    )
