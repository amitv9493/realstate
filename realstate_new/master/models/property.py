from django.db import models
from django.utils import timezone

from realstate_new.utils.base_models import TrackingModel

from .features import PropertyFeature
from .types import PropertyStatus
from .types import PropertyType


class Property(TrackingModel):
    # address
    delivery_line = models.CharField(max_length=255, default="")
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip = models.CharField(max_length=50)
    street = models.CharField(max_length=50)

    # cordinates
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    # listing meta info
    price = models.PositiveIntegerField("Current Listing Price", default=0)
    listing_type = models.CharField(
        max_length=50,
        choices=PropertyType.choices,
        default=PropertyType.OTHER,
    )
    listing_date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=50,
        choices=PropertyStatus,
        default=PropertyStatus.AVAILABLE,
    )
    lotsize_sqft = models.PositiveIntegerField(null=True, blank=True, default=0)
    lotsize_acres = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    size = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    year_built = models.PositiveIntegerField(default=0)
    mls_number = models.IntegerField(default=0)
    description = models.TextField(default="")
    features = models.ManyToManyField(PropertyFeature, null=True)

    def __str__(self):
        return f"{self.id} {self.status}"

    # Contact Information: Contact details for the listing agent (phone number, email).
