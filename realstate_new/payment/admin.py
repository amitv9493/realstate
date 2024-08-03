from django.contrib import admin

from .models import PayPalPayementHistory
from .models import Transaction
from .models import Wallet


@admin.register(PayPalPayementHistory)
class PayPalPayementHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date_created",
        "transmission_id",
        "transmission_time",
        "event_body",
        "valid",
    )
    list_filter = ("date_created", "transmission_time", "valid")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "balance", "user")
    list_filter = ("user",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "amount",
        "transaction_type",
        "timestamp",
    )
    list_filter = ("wallet", "timestamp")
