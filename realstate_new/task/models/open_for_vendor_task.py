from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from realstate_new.master.models.property import Property

from .basetask import BaseTask


class VendorType(models.Model):
    vendor = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.vendor


class OpenForVendorTask(BaseTask):
    property_address = GenericRelation(Property)

    open_for_vendor = models.ManyToManyField(VendorType, null=True, blank=True)
    vendor_name = models.CharField(max_length=50, default="", blank=True)
    vendor_phone = models.CharField(max_length=50, default="", blank=True)
    duration = models.DurationField(null=True, blank=True)

    @property
    def type_of_task(self):
        return "OpenForVendor"
