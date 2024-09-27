from django.db import models

from realstate_new.task import models as tasks


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


JOB_TYPE_MAPPINGS = {
    "LockBoxBS": tasks.LockBoxTaskBS,
    "LockBoxIR": tasks.LockBoxTaskIR,
    "Showing": tasks.ShowingTask,
    "OpenHouse": tasks.OpenHouseTask,
    "Runner": tasks.RunnerTask,
    "Sign": tasks.SignTask,
    "Professional": tasks.ProfessionalServiceTask,
}
