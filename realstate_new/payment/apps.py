from django.apps import AppConfig


class PaymentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "realstate_new.payment"

    def ready(self) -> None:
        from .celery_tasks import celery_create_payment  # noqa: F401

        return super().ready()
