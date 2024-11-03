from django.conf import settings
from django.db import models

from realstate_new.utils.base_models import GenericModel

from .choices import PaymentStatusChoices
from .choices import PaymentTypeChoics


class Transcation(GenericModel):
    nonce = models.TextField(default="")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    transcation_id = models.CharField(max_length=255, default="")
    transcation_type = models.CharField(
        choices=PaymentTypeChoics.choices,
        max_length=50,
    )
    status = models.CharField(
        max_length=50,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.INITIATED,
    )
    created_at = models.DateTimeField(auto_now_add=False)
