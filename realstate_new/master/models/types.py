from django.db import models


class PropertyType(models.TextChoices):
    SFH = "SFH", "Single Family Home"
    CONDO = "CONDO", "Condo"
    APT = "APT", "Apartment"
    COMM = "COMM", "Commercial"


class PropertyStatus(models.TextChoices):
    AVAILABLE = "Available", "Available"
    UC = "Under Contract", "Under Contract"
    SOLD = "Sold", "Sold"
