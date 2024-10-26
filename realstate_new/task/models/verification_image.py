from django.db import models

from realstate_new.utils.base_models import GenericModel


def get_upload_to(instance, filename):
    task = instance.content_object
    prefix = "verification-images"
    return f"{prefix}/{task.created_by.email}/{task.type_of_task}/{instance.object_id}/{filename}"


class VerificationDocument(GenericModel):
    image = models.ImageField(upload_to=get_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return super().__str__()
