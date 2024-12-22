from django.db import models


class LockBoxType(models.TextChoices):
    SUPRA = "SUPRA", "SUPRA"
    KEYPAD_ENTRY = "KEYPAD_ENTRY", "KEYPAD ENTRY"
    CONTRACTOR = "CONTRACTOR", "CONTRACTOR"
    OTHER = "OTHER", "OTHER"


class TaskTypeChoices(models.TextChoices):
    install = "INSTALL", "Install"
    remove = "REMOVE", "Remove"
    buy = "BUY", "Buy"
    sell = "SELL", "Sell"


class RunnerTaskType(models.TextChoices):
    ATTEND_CLOSING = "ATTEND_CLOSING", "Attend closing for agent"
    PAPERWORK = "PAPERWORK", "Paperwork Courier / Paperwork in Office"
    DD = "DOCUMENT_DELIVERY", "Document Delivery"
    NOTARY_SERVICE = "NOTARY_SERVICE", "Notary Services"
    PROPERTY_INSPECTION = "PROPERTY_INSPECTION", "Property Inspections"
    TRANSLATOR = "TRANSLATOR", "Translator for secondary Language"
    HOME_ERRANDS = "HOME_ERRANDS", "Homes errands"
    OTHER = "OTHER", "Other"


class JobType(models.TextChoices):
    apply = "APPLY", "Apply"
    claim = "CLAIM", "Claim"


class BrokerageType(models.TextChoices):
    MY_BROKERAGE = (
        "MY-BROKERAGE",
        "My Brokerage",
    )

    OTHER_BROKERAGE = (
        "OTHER-BROKERAGE",
        "All Other Brokerages",
    )


class ProfessionalServiceType(models.TextChoices):
    photography = "PHOTOGRAPHY", "Photography"
    cleaning = "CLEANING", "Cleaning"
    repair = "REPAIR", "Repair"
    inspection = "INSPECTION", "Inspection"
    other = "OTHER", "other"
    home_staging = "HOME STAGING", "Home Staging"


class SignTaskType(models.TextChoices):
    install = "INSTALL", "Install"
    remove = "REMOVE", "Remove"


class TaskStatusChoices(models.TextChoices):
    CREATED = "CREATED", "Task Created"
    ASSIGNED = "ASSIGNED", "Task Assigned"
    STARTED = "STARTED", "Task Started"
    VERIFIED = "VERIFIED", "Task Verified"
    CREATER_CANCELLED = "CREATER_CANCELLED", "Task Cancelled by creater"
    ASSIGNER_CANCELLED = "ASSIGNER_CANCELLED", "Task Cancelled by assigner"
    REASSIGNED = "REASSIGNED", "Task Reassigned"
    MARK_COMPLETED = "MARK_COMPLETED", "Task Marked Completed"
