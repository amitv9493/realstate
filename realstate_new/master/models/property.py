from django.db import models
from django.utils import timezone

from realstate_new.utils.base_models import TrackingModel

from .features import PropertyFeature
from .types import PropertyStatus
from .types import PropertyType


class Property(TrackingModel):
    property_address = models.TextField(default="")
    property_type = models.CharField(
        max_length=50,
        choices=PropertyType.choices,
        default=PropertyType.OTHER,
    )
    listing_date = models.DateField(default=timezone.now())
    status = models.CharField(
        max_length=50,
        choices=PropertyStatus,
        default=PropertyStatus.AVAILABLE,
    )
    price = models.PositiveIntegerField("Current Listing Price", default=0)
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    lot_size = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    square_footage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    year_built = models.PositiveIntegerField(default=0)
    mls_number = models.IntegerField(default=0)
    description = models.TextField(default="")
    features = models.ManyToManyField(PropertyFeature)
    api_response = models.JSONField()

    def __str__(self):
        return f"{self.id} = {self.property_type} - {self.status}"

    # will fetch it from the user created this property record
    # Contact Information: Contact details for the listing agent (phone number, email).
