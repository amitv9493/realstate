from typing import Any

from django.contrib import admin


class CustomModelAdmin(admin.ModelAdmin):
    """Saves who created the the model instance.
    Use only when `created_by` field is present in the Model"""

    readonly_fields = ("created_by",)

    def save_model(
        self,
        request: Any,
        obj: Any,
        form: Any,
        change: Any,
    ) -> None:
        obj.created_by_id = request.user.id
        return super().save_model(request, obj, form, change)
