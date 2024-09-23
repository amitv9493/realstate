from django.db import models

from .basetask import BaseTask


class OpenHouseTask(BaseTask):
    access_information = models.TextField()
    open_house_instructions = models.TextField()

    @property
    def type_of_task(self):
        return "OpenHouse"
