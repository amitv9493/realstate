from django.conf import settings
from django.db import models

from realstate_new.utils.base_models import TrackingModel

from .choices import PaymentTypeChoics
from .choices import PayymentStatusChoices


class Transcation(TrackingModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    transcation_id = models.CharField(max_length=255)
    transcation_type = models.CharField(
        choices=PaymentTypeChoics.choices,
        max_length=50,
    )
    status = models.CharField(max_length=50, choices=PayymentStatusChoices.choices)
