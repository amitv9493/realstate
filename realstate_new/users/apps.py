import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "realstate_new.users"
    verbose_name = _("Users")

    def ready(self):
        from .celery_tasks import get_users_count  # noqa: F401

        with contextlib.suppress(ImportError):
            import realstate_new.users.signals  # noqa: F401
