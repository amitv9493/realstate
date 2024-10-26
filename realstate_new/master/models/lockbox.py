from django.db import models

from .types import LockBoxType


class LockBox(models.Model):
    lockbox_type = models.CharField(
        max_length=50,
        choices=LockBoxType.choices,
        default=LockBoxType.OTHER,
    )
    lockbox_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )
    additional_info = models.TextField(default="", blank=True)

    def __str__(self):
        return f"{self.lockbox_type}-{self.lockbox_code}"
