from django.db import models


class PropertyType(models.TextChoices):
    SFH = "SFH", "Single Family Home"
    CONDO = "CONDO", "Condo"
    APT = "APT", "Apartment"
    COMM = "COMM", "Commercial"
    OTHER = "OTHER", "Other"


class LockBoxType(models.TextChoices):
    SUPRA = "SUPRA", "SUPRA"
    KEYPAD_ENTRY = "KEYPAD_ENTRY", "KEYPAD ENTRY"
    CONTRACTOR = "CONTRACTOR", "CONTRACTOR"
    OTHER = "OTHER", "OTHER"
