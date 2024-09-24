from django.db import models

from .basetask import BaseTask
from .choices import LockBoxType
from .choices import TaskTypeChoices


class LockBoxTask(BaseTask):
    task_type = models.CharField(max_length=50, choices=TaskTypeChoices.choices)
    lockbox_code = models.CharField(max_length=50)
    instructions = models.TextField()
    lockbox_type = models.CharField(
        max_length=50,
        choices=LockBoxType.choices,
    )
    sign_option = models.BooleanField(default=False)
    sign_address = models.TextField(blank=True)

    # if task_type is REMOVE
    pickup_address = models.TextField(blank=True)
    dropoff_address = models.TextField(blank=True)

    # if task_type is INSTALL
    lockbox_collection_address = models.TextField(blank=True)
    installation_address = models.TextField(blank=True)
    installation_location = models.TextField(blank=True)

    # if task_type is BUY

    # in case of buy and sell
    price = models.PositiveIntegerField(blank=True)

    include_sign = models.BooleanField(null=True, blank=True)

    @property
    def type_of_task(self):
        return "Lockbox"


class LockBoxTaskIR(LockBoxTask):
    class LockBoxTaskIRManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(task_type__in=["INSTALL", "REMOVE"])

    class Meta:
        proxy = True
        verbose_name = "Lock Box (Install / Remove)"
        verbose_name_plural = "Lock Box (Install / Remove)"

    objects = LockBoxTaskIRManager()


class LockBoxTaskBS(LockBoxTask):
    class LockBoxTaskBSManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(task_type__in=["BUY", "SELL"])

    class Meta:
        proxy = True
        verbose_name = "Lock Box (Buy / Sell)"

    objects = LockBoxTaskBSManager()


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
