from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "object_id",
        "event",
        "content_type",
        "is_read",
    )
    list_filter = (
        "user",
        "object_id",
        "event",
        "content_type",
        "is_read",
    )
