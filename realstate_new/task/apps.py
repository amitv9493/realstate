from django.apps import AppConfig


class TaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "realstate_new.task"
    label = "task"

    def ready(self) -> None:
        from .celery_tasks import check_task_expiry  # noqa: F401

        return super().ready()
