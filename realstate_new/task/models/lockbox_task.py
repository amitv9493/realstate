from django.db import models

from .basetask import BaseTask
from .choices import TaskTypeChoices


class LockBoxTask(BaseTask):
    task_type = models.CharField(max_length=50, choices=TaskTypeChoices.choices)

    lockbox = models.OneToOneField(
        "master.LockBox",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    # Address related fields.

    # if task_type is BUY SELL
    pickup_address = models.OneToOneField(
        "master.Property",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    # if task_type is INSTALL/ REMOVE
    installation_or_remove_address = models.OneToOneField(
        "master.Property",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )

    include_sign = models.BooleanField(
        "Include Sign",
        null=True,
        blank=True,
    )
    remove_sign = models.BooleanField(
        "Include Sign",
        null=True,
        blank=True,
    )

    @property
    def type_of_task(self):
        if self.task_type in {"INSTALL", "REMOVE"}:
            return "LockBoxIR"
        if self.task_type in {"BUY", "SELL"}:
            return "LockBoxBS"
        return ""


class LockBoxTaskIR(LockBoxTask):
    class LockBoxTaskIRManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(task_type__in=["INSTALL", "REMOVE"])

    class Meta:
        proxy = True
        verbose_name = "Lock Box (Install / Remove)"
        verbose_name_plural = "Lock Box (Install / Remove)"

    objects = LockBoxTaskIRManager()

    @property
    def type_of_task(self):
        return "LockBoxIR"


class LockBoxTaskBS(LockBoxTask):
    class LockBoxTaskBSManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(task_type__in=["BUY", "SELL"])

    class Meta:
        proxy = True
        verbose_name = "Lock Box (Buy / Sell)"

    objects = LockBoxTaskBSManager()

    @property
    def type_of_task(self):
        return "LockBoxBS"
