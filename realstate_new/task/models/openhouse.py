from django.db import models

from .basetask import BaseTask


class OpenHouseTask(BaseTask):
    property_address = models.OneToOneField(
        "master.Property",
        on_delete=models.CASCADE,
        null=True,
    )
    access_information = models.TextField()
    open_house_instructions = models.TextField()
    listing_agent = models.BooleanField(null=True, blank=True, default=False)
    hosting_agent = models.BooleanField(null=True, blank=True, default=False)
    duration = models.DurationField(null=True, blank=True)

    @property
    def type_of_task(self):
        return "OpenHouse"
