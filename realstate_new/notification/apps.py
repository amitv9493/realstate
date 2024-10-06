from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "realstate_new.notification"

    def ready(self) -> None:
        return super().ready()
