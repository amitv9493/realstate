from django.apps import AppConfig
from django.db.models.signals import post_save


class TaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "realstate_new.task"
    label = "task"

    def ready(self) -> None:
        from realstate_new.master.models.types import JOB_TYPE_MAPPINGS

        from .receivers import send_notification_upon_task_acceptance

        for job_model in JOB_TYPE_MAPPINGS.values():
            post_save.connect(send_notification_upon_task_acceptance, sender=job_model)

        return super().ready()
