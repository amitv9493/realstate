from django.db import models


class LockBoxType(models.TextChoices):
    SUPRA = "SUPRA", "SUPRA"
    KEYPAD_ENTRY = "KEYPAD ENTRY", "KEYPAD ENTRY"
    CONTRACTOR = "CONTRACTOR", "CONTRACTOR"


class TaskTypeChoices(models.TextChoices):
    install = "INSTALL", "Install"
    remove = "REMOVE", "Remove"
    buy = "BUY", "Buy"
    sell = "SELL", "Sell"


class RunnerTaskType(models.TextChoices):
    dd = "DOCUMENT DELIVERY", "Document Delivery"
    key_drop_off = "KEY DROP OFF", "Key Drop Off"
    key_pick_off = "KEY PICK OFF", "Key Pick Off"
    property_check = "PROPERTY CHECK", "Property Check"
    other = "OTHER", "Other"
    meet_delivery_vendor = "MEET DELIVERY VENDOR", "Meet delivery or Vendor"
    attend_closing = "ATTEND CLOSING", "Attend closing for agent"
    take_photos = (
        "TAKE PHOTOS",
        "Take photos of Inside / Outside of house, separate from professional photos",
    )
    paperwork = "PAPERWORK", "Paperwork Courier / Paperwork in Office"


class JobType(models.TextChoices):
    apply = "APPLY", "Apply"
    claim = "CLAIM", "Claim"


class BrokerageType(models.TextChoices):
    my_brokerage = (
        "MY-BROKERAGE",
        "My Brokerage",
    )

    other_brokerage = (
        "OTHER-BROKERAGE",
        "All Other Brokerages",
    )


class ProfessionalServiceType(models.TextChoices):
    photography = "PHOTOGRAPGY", "Photography"
    cleaning = "CLEANING", "Cleaning"
    repair = "REPAIR", "Repair"
    inspection = "INSPECTION", "Inspection"
    other = "OTHER", "other"
    home_staging = "HOME STAGING", "Home Staging"


class SignTaskType(models.TextChoices):
    install = "INSTALL", "Install"
    remove = "REMOVE", "Remove"
