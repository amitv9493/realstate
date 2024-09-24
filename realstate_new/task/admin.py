from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import LockBox
from .models import LockBoxTaskBS
from .models import LockBoxTaskIR
from .models import OpenHouseTask
from .models import ProfessionalServiceTask
from .models import RunnerTask
from .models import ShowingTask
from .models import SignTask
from .models import ThirdPartyCall


class BaseTaskAdmin(admin.ModelAdmin):
    list_display = (
        "task_time",
        "client_name",
        "payment_amount",
        "is_completed",
        "job_type",
        "assigned_to",
    )
    list_filter = ("is_completed", "task_time", "job_type")
    search_fields = ("property", "client_name", "client_email")
    date_hierarchy = "task_time"
    readonly_fields = ("created_at", "updated_at", "created_by")

    fieldsets = (
        (
            _("Task Information"),
            {
                "fields": (
                    "property",
                    "task_time",
                    "job_type",
                    "apply_deadline",
                    "brokerage",
                ),
            },
        ),
        (
            _("Client Information"),
            {
                "fields": (
                    "client_name",
                    "client_phone",
                    "client_email",
                    "show_client_info",
                ),
            },
        ),
        (
            _("Payment Details"),
            {"fields": ("payment_amount",)},
        ),
        (_("Assignment"), {"fields": ("assigned_to", "is_completed")}),
        (
            _("Additional Information"),
            {
                "fields": (
                    "lockbox_type",
                    "vacant",
                    "pets",
                    "concierge",
                    "alarm_code",
                    "gate_code",
                    "notes",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ShowingTask)
class ShowingTaskAdmin(BaseTaskAdmin):
    fieldsets = (
        *BaseTaskAdmin.fieldsets,
        (
            _("Showing Details"),
            {"fields": ("access_information",)},
        ),
    )


@admin.register(OpenHouseTask)
class OpenHouseTaskAdmin(BaseTaskAdmin):
    fieldsets = (
        *BaseTaskAdmin.fieldsets,
        (
            _("Open House Details"),
            {"fields": ("access_information", "open_house_instructions")},
        ),
    )


@admin.register(LockBoxTaskIR)
class LockboxTaskIRAdmin(BaseTaskAdmin):
    fieldsets = (
        *BaseTaskAdmin.fieldsets,
        (
            _("Lockbox Details"),
            {"fields": ("task_type", "lockbox_code", "instructions", "include_sign")},
        ),
        (
            "INSTALL",
            {
                "fields": (
                    "lockbox_collection_address",
                    "installation_address",
                    "installation_location",
                ),
            },
        ),
        ("REMOVE", {"fields": ("pickup_address", "dropoff_address")}),
    )


class LockBoxAdminInline(admin.StackedInline):
    model = LockBox
    fk_name = "lockbox_task"
    extra = 1


@admin.register(LockBoxTaskBS)
class LockboxTaskBSAdmin(BaseTaskAdmin):
    fieldsets = (
        *BaseTaskAdmin.fieldsets,
        (
            _("Lockbox Details"),
            {
                "fields": (
                    "task_type",
                    "lockbox_code",
                    "instructions",
                    "price",
                    "pickup_address",
                    "include_sign",
                ),
            },
        ),
    )

    inlines = [LockBoxAdminInline]


@admin.register(SignTask)
class SignTaskAdmin(BaseTaskAdmin):
    fieldsets = (
        *BaseTaskAdmin.fieldsets,
        (
            _("Sign Details"),
            {
                "fields": (
                    "task_type",
                    "sign_type",
                    "instructions",
                    "collection_address",
                    "dropoff_address",
                ),
            },
        ),
    )


@admin.register(RunnerTask)
class RunnerTaskAdmin(BaseTaskAdmin):
    fieldsets = (
        *BaseTaskAdmin.fieldsets,
        (
            _("Runner Details"),
            {
                "fields": (
                    "task_type",
                    "instructions",
                ),
            },
        ),
        (
            _("Vendor Details"),
            {
                "fields": (
                    "vendor_name",
                    "vendor_phone",
                    "vendor_company_name",
                    "vebdor_notes",
                ),
            },
        ),
        (_("In case of Paper work"), {"fields": ("pickup_address", "dropoff_address")}),
    )


@admin.register(ProfessionalServiceTask)
class ProfessionalServiceTaskAdmin(BaseTaskAdmin):
    fieldsets = (
        *BaseTaskAdmin.fieldsets,
        (
            _("Service Details"),
            {
                "fields": (
                    "service_type",
                    "service_provider_name",
                    "service_provider_phone",
                    "service_provider_email",
                    "service_instructions",
                ),
            },
        ),
    )


@admin.register(ThirdPartyCall)
class ThirdPartyCallAdmin(admin.ModelAdmin):
    list_display = (
        "shortened_endpoint",
        "status_code",
        "date_created",
    )
    ordering = ("-date_created",)
