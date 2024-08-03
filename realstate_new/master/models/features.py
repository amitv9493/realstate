from django.db import models


class PropertyFeature(models.Model):
    feature_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return super().__str__()
