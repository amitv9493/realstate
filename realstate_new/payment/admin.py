from django.contrib import admin

from .models import PayPalPayementHistory


@admin.register(PayPalPayementHistory)
class PayPalPayementHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date_created",
    )
    list_filter = ("date_created",)
