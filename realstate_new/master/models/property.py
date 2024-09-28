from django.db import models

from realstate_new.utils.base_models import TrackingModel


class Property(TrackingModel):
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=50)
    street = models.CharField(max_length=255)

    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.street}"
