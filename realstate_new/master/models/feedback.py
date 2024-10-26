from django.db import models

from realstate_new.utils.base_models import TrackingModel

from .types import FeedbackType


class Feedback(TrackingModel):
    feedback = models.TextField()
    feedback_type = models.CharField(
        choices=FeedbackType.choices,
        default=FeedbackType.GENERAL,
        max_length=50,
    )

    def __str__(self) -> str:
        return f"{self.created_by.get_full_name()}-{self.feedback_type}"
