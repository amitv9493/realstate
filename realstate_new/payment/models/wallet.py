import logging

from django.conf import settings
from django.db import models
from django.db import transaction

from realstate_new.payment.errors import InsufficientAmountErrorError

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

    def add_money(self, amount):
        try:
            with transaction.atomic():
                self.balance += amount
                self.save()
                self.transaction.create(amount=amount, transaction_type="deposit")
                return True
        except Exception as e:
            msg = f"An Error occured while adding money from waller {e}"
            logger.exception(msg)
            return False

    def _has_enough_amount(self, amount):
        if not self.balance >= amount:
            raise InsufficientAmountErrorError

    def deduct_amount(self, amount):
        with transaction.atomic():
            msg = f"Wallet Balance {self.balance}"
            logger.info(msg)
            self._has_enough_amount(amount)
            self.balance -= amount
            self.save()
            self.transaction.create(amount=amount, transaction_type="withdrawal")


class Transaction(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transaction",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20,
        choices=[("deposit", "Deposit"), ("withdrawal", "Withdrawal")],
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - {self.amount}"
