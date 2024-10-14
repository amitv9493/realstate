from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from realstate_new.utils.base_models import TrackingModel


class LockBoxType(models.TextChoices):
    SUPRA = "SUPRA", "SUPRA"
    KEYPAD_ENTRY = "KEYPAD_ENTRY", "KEYPAD ENTRY"
    CONTRACTOR = "CONTRACTOR", "CONTRACTOR"
    OTHER = "OTHER", "OTHER"


class Property(TrackingModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    task = GenericForeignKey("content_type", "object_id")

    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=50)
    street = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    # other info
    vacant = models.BooleanField(default=False, null=True)
    pets = models.BooleanField(default=False, null=True)
    concierge = models.BooleanField(default=False, null=True)
    alarm_code = models.CharField(max_length=50, default="", blank=True)
    gate_code = models.CharField(max_length=50, default="", blank=True)

    lockbox_type = models.CharField(
        max_length=50,
        choices=LockBoxType.choices,
        default=LockBoxType.OTHER,
        blank=True,
    )

    def __str__(self):
        return f"{self.street}"

    class Meta:
        indexes = [models.Index(fields=["id"])]
