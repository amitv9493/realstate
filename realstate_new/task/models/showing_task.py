from django.db import models

from .basetask import BaseTask


class ShowingTask(BaseTask):
    access_information = models.TextField()

    @property
    def type_of_task(self):
        return "Showing"
