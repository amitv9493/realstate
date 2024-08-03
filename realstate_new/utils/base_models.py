from django.contrib.auth import get_user_model
from django.db import models


class TrackingModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="%(class)s_creator",
        null=True,
    )

    class Meta:
        abstract = True
