from django.db import models


class PayPalPayementHistory(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    transmission_id = models.CharField(max_length=255)
    transmission_time = models.DateTimeField()
    event_body = models.JSONField()
    valid = models.BooleanField(default=False)

    def __str__(self) -> str:
        return super().__str__()
