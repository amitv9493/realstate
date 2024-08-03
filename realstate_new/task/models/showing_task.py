from django.db import models

from .basetask import BaseTask


class ShowingTask(BaseTask):
    access_information = models.TextField()
