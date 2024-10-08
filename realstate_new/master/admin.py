from typing import Any

from django.contrib import admin

from .models import Property
from .models import PropertyFeature


@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ("id", "feature_name")


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
