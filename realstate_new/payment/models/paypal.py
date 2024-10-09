import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class TranscationTypeChoice(models.TextChoices):
    INITIATED = "INITIATED", "Initiated"
    FAILED = "FAILED", "Failed"
    COMPLETED = "COMPLETED", "Completed"
    RECEIVED = "RECEIVED", "Received"


class PayPalPayementHistory(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    payble_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payble",
    )
    payble_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="receiveble",
    )
    transcation_type = models.CharField(
        max_length=50,
        choices=TranscationTypeChoice.choices,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_id = models.CharField(max_length=255, default="")
    retry_attempt = models.PositiveIntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    error_message = models.TextField(default="")

    def __str__(self) -> str:
        return super().__str__()


class PaymentBatch(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_processing = models.ManyToManyField(PayPalPayementHistory)
    batch_id = models.CharField(max_length=50)

    def __str__(self) -> str:
        return super().__str__()
