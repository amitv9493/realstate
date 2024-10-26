from django.contrib.postgres.fields import ArrayField
from django.db import models

from realstate_new.utils.base_models import TrackingModel

from .types import ProfessionalServiceSkillChoices


class ProfessioanlVendorInquiry(TrackingModel):
    # client phone and email will be fetched from the current user.
    # just in case user wants to add another email and phone.
    client_phone = ArrayField(
        base_field=models.CharField(max_length=50),
        null=True,
        blank=True,
    )
    client_email = ArrayField(base_field=models.EmailField(), null=True, blank=True)
    preferred_name = models.CharField(max_length=50, default="", blank=True)
    preferred_method_of_contact = models.CharField(
        choices=[
            (
                "PHONE",
                "PHONE",
            ),
            (
                "EMAIL",
                "EMAIL",
            ),
        ],
        default="EMAIL",
    )
    service_skill = models.CharField(
        max_length=50,
        choices=ProfessionalServiceSkillChoices.choices,
        default=ProfessionalServiceSkillChoices.PH,
    )
    mile_radius_preference = models.CharField(
        "Area Covered",
        max_length=50,
        default="",
        blank=True,
    )
    additional_notes = models.TextField(default="", blank=True)

    def __str__(self) -> str:
        return f"{self.created_by.get_full_name()}"
