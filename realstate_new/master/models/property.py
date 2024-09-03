from django.db import models

from realstate_new.utils.base_models import TrackingModel

from .features import PropertyFeature
from .types import PropertyStatus
from .types import PropertyType


class Property(TrackingModel):
    property_address = models.TextField()
    property_type = models.CharField(
        max_length=50,
        choices=PropertyType.choices,
    )
    listing_date = models.DateField()
    status = models.CharField(
        max_length=50,
        choices=PropertyStatus,
        default=PropertyStatus.AVAILABLE,
    )
    price = models.PositiveIntegerField("Current Listing Price")
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    lot_size = models.DecimalField(max_digits=5, decimal_places=3)
    square_footage = models.DecimalField(max_digits=5, decimal_places=3)
    year_built = models.PositiveIntegerField()
    mls_number = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=255, blank=True)
    features = models.ManyToManyField(PropertyFeature)

    def __str__(self):
        return f"{self.id} = {self.property_type} - {self.status}"

    # will fetch it from the user created this property record
    # Contact Information: Contact details for the listing agent (phone number, email).
