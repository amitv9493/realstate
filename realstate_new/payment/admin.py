from django.contrib import admin

from .models import PayPalPayementHistory
from .models import StripeTranscation


@admin.register(PayPalPayementHistory)
class PayPalPayementHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date_created",
    )
    list_filter = ("date_created",)


@admin.register(StripeTranscation)
class StripeTranscationAdmin(admin.ModelAdmin):
    list_display = ["content_type", "amt", "identifier"]
