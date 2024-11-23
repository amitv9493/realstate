from django.contrib import admin

from .fcm import FCM
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "object_id",
        "event",
        "content_type",
        "is_read",
        "is_sent",
    )
    list_filter = (
        "user",
        "object_id",
        "event",
        "content_type",
        "is_read",
    )

    @admin.action(description="Re-trigger Notification")
    def retrigger_notification(self, request, queryset):
        fcm = FCM()
        for q in queryset:
            message = fcm.build_common_message(
                title=q.title,
                nody=q.body,
                token=q.regis,
            )
            fcm.send_fcm_message(message)
