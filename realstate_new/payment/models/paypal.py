from django.conf import settings
from django.db import models


class TranscationTypeChoice(models.TextChoices):
    DIPOSIT = "DIPOSIT", "DIPOSIT"
    WITHDRAW = "WITHDRAW", "WITHDRAW"


class PayPalPayementHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transactions",
    )
    date_created = models.DateTimeField(auto_now_add=True)
    transcation_type = models.CharField(
        max_length=50,
        choices=TranscationTypeChoice.choices,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_id = models.CharField(max_length=255, default="")
    success = models.BooleanField(default=False)

    def __str__(self) -> str:
        return super().__str__()
