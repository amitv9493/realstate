from django.db.models import TextChoices


class PaymentTypeChoics(TextChoices):
    PAYMENT = "PAYMENT", "PAYMENT"
    PAYOUT = "PAYOUT", "PAYOUT"


class PayymentStatusChoices(TextChoices):
    SUCCESS = "SUCCESS", "SUCCESS"
    FAILURE = "FAILURE", "FAILURE"
    INITIATED = "INITIATED", "INITIATED"
