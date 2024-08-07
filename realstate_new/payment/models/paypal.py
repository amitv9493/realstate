from django.db import models

from .wallet import Wallet


class PayPalPayementHistory(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transmission_id = models.CharField(max_length=255)
    transmission_time = models.DateTimeField(auto_now_add=True)
    event_body = models.JSONField()
    valid = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    transcation_type = models.CharField(
        max_length=50,
        choices=[("WITHDRAW", "WITHDRAW"), ("DIPOSIT", "DIPOSIT")],
    )

    def __str__(self) -> str:
        return super().__str__()
