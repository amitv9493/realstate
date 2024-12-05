from django.db import models

from realstate_new.notification.models import Notification
from realstate_new.utils.base_models import GenericModel


class TranscationStatus(models.TextChoices):
    SUCCESS = "SUCCESS", "SUCCESS"
    FAILED = "FAILED", "FAILED"
    PROCESSING = "PROCESSING", "PROCESSING"
    INITIATED = "INITIATED", "INITIATED"


class TxnType(models.TextChoices):
    PAYIN = "PAYIN", "PAYIN"
    PAYOUT = "PAYOUT", "PAYOUT"


class StripeTranscation(GenericModel):
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    amt = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, choices=TranscationStatus.choices)
    txn_type = models.CharField(
        max_length=50,
        choices=TxnType.choices,
        default=TxnType.PAYIN,
    )
    identifier = models.TextField(default="")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == TranscationStatus.SUCCESS and self.txn_type == TxnType.PAYIN:
            self.content_object.payment_verified = True
            self.content_object.save(update_fields=["payment_verified"])
            Notification.objects.create(
                event="CREATED",
                content_object=self.content_object,
                user=self.user,
            )
