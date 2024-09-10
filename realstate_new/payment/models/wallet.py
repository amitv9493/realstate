import logging

from django.conf import settings
from django.db import models
from django.db import transaction

from realstate_new.payment.errors import InsufficientAmountError

logger = logging.getLogger(__name__)


class Wallet(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    def __str__(self):
        return f"{self.user.username}-{self.balance}"

    def add_amount(self, amount):
        with transaction.atomic():
            self.balance += amount
            self.save(update_fields=["balance"])

    def _has_enough_amount(self, amount):
        if not self.balance >= amount:
            raise InsufficientAmountError

    def deduct_amount(self, amount):
        with transaction.atomic():
            msg = f"Wallet Balance {self.balance}"
            logger.info(msg)
            self._has_enough_amount(amount)
            self.balance -= amount
            self.save(update_fields=["balance"])
            self.transaction.create(amount=amount, transcation_type="WITHDRAW")
