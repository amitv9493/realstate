from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class JobApplication(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    task_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "task_id")

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "PENDING"),
            ("ACCEPTED", "ACCEPTED"),
            ("REJECTED", "REJECTED"),
            ("CLAIMED", "CLAIMED"),
        ],
        default="PENDING",
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="application",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "task_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["task_id", "content_type", "applicant"],
                name="unique-application",
                violation_error_message="The record already exists.",
            ),
        ]

    def __str__(self):
        return f"{self.content_type!s} {self.status}"
