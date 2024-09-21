from django.db import models


class PropertyType(models.TextChoices):
    SFH = "SFH", "Single Family Home"
    CONDO = "CONDO", "Condo"
    APT = "APT", "Apartment"
    COMM = "COMM", "Commercial"
    OTHER = "OTHER", "Other"


class PropertyStatus(models.TextChoices):
    AVAILABLE = "AVAIABLRE", "Available"
    UC = "UNDER CONTRACT", "Under Contract"
    SOLD = "SOLD", "Sold"
    OTHER = "OTHER", "Other"
