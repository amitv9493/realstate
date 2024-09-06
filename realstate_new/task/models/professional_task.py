from django.db import models

from .basetask import BaseTask
from .choices import ProfessionalServiceType


class ProfessionalServiceTask(BaseTask):
    service_type = models.CharField(
        max_length=50,
        choices=ProfessionalServiceType.choices,
    )
    service_provider_name = models.CharField(max_length=100)
    service_provider_phone = models.CharField(max_length=20)
    service_provider_email = models.EmailField()
    service_instructions = models.TextField()
