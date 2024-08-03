from celery import shared_task

from .paypal import create_payment


@shared_task(bind=True)
def start_create_payment(self):
    create_payment()
    return True
