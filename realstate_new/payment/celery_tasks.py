from celery import shared_task

from realstate_new.api.payment.hyperwallet import HyperwalletPayoutHandler

handler = HyperwalletPayoutHandler()


@shared_task(bind=True)
def celery_create_payment(self, task_instance):
    if task_instance.payment_amount and task_instance > 0:
        handler.create_payment(task=task_instance, amount=task_instance.payment_amount)
