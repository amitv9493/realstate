from django.contrib import admin

from .models import PayPalPayementHistory
from .models import Wallet


@admin.register(PayPalPayementHistory)
class PayPalPayementHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "date_created",
    )
    list_filter = ("date_created",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "balance", "user")
    list_filter = ("user",)
