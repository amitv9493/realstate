from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from realstate_new.master.models import Property

from .basetask import BaseTask


class ShowingTask(BaseTask):
    property_address = GenericRelation(Property)
    access_information = models.TextField(blank=True, default="")

    @property
    def type_of_task(self):
        return "Showing"
