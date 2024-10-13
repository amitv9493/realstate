from django.db import models

from .basetask import BaseTask
from .choices import TaskTypeChoices


class LockBoxTask(BaseTask):
    task_type = models.CharField(max_length=50, choices=TaskTypeChoices.choices)
    lockbox_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )  # remove this field in future

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


class LockBox(models.Model):
    name = models.CharField(max_length=50)
    lockbox_type = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    lockbox_task = models.OneToOneField(
        LockBoxTask,
        on_delete=models.CASCADE,
        related_name="lockbox",
        verbose_name="Lock Boxes",
    )

    def __str__(self) -> str:
        return super().__str__()
