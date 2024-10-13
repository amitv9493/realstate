from django.db import models

from .basetask import BaseTask
from .choices import ProfessionalServiceType


class ProfessionalServiceTask(BaseTask):
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    website = models.URLField(blank=True)
    service_type = models.CharField(
        max_length=50,
        choices=ProfessionalServiceType.choices,
    )

    @property
    def type_of_task(self):
        return "Professional"
