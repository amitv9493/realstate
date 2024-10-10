import os
from datetime import timedelta

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("realstate_new")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-task-expiry-cronjob": {
        "task": "realstate_new.task.celery_tasks.check_task_expiry",
        "schedule": timedelta(minutes=1).total_seconds(),
        "args": [],
    },
    "job-reminder-24-hour": {
        "task": "realstate_new.task.celery_tasks.job_reminder",
        "schedule": timedelta(minutes=1).total_seconds(),
        "args": [timedelta(hours=24).total_seconds()],
    },
    "job-reminder-1-hour": {
        "task": "realstate_new.task.celery_tasks.job_reminder",
        "schedule": timedelta(minutes=1).total_seconds(),
        "args": [timedelta(hours=1).total_seconds()],
    },
}
