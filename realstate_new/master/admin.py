from typing import Any

from django.contrib import admin

from realstate_new.utils.admin import CustomModelAdmin

from .models import Feedback
from .models import LockBox
from .models import ProfessioanlVendorInquiry
from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_filter = (
        "created_at",
        "updated_at",
        "created_by",
    )
    date_hierarchy = "created_at"

    readonly_fields = ("created_by",)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        obj.created_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(LockBox)
class LockBoxAdmin(admin.ModelAdmin):
    pass


@admin.register(ProfessioanlVendorInquiry)
class ProfessioanlVendorInquiryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "client_phone",
        "client_email",
        "preferred_name",
        "preferred_method_of_contact",
        "service_skill",
        "mile_radius_preference",
        "additional_notes",
    )
    list_filter = ("created_at", "updated_at", "created_by")
    date_hierarchy = "created_at"


@admin.register(Feedback)
class FeedbackAdmin(CustomModelAdmin):
    list_display = ["created_by", "feedback_type", "created_at"]
    list_filter = list_display
