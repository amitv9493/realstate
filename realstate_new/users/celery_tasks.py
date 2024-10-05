from celery import shared_task
from django.contrib.auth import get_user_model


@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return get_user_model().objects.count()
