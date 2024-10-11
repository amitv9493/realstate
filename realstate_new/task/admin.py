from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from realstate_new.task.models.sign_task import SignTask

from .models import LockBoxTaskBS
from .models import LockBoxTaskIR
from .models import OpenHouseTask
from .models import ProfessionalServiceTask
from .models import RunnerTask
from .models import ShowingTask
from .models import ThirdPartyCall


class BaseTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task_time",
        "client_name",
        "payment_amount",
        "asap",
        "is_verified",
        "job_type",
        "assigned_to",
        "created_by",
    )
    list_filter = (
        "is_verified",
        "task_time",
        "job_type",
        "asap",
    )
    search_fields = ("property", "client_name", "client_email")
    date_hierarchy = "task_time"
    readonly_fields = ("created_at", "updated_at", "created_by")

    fieldsets = (
        (
            _("Task Information"),
            {
                "fields": (
                    "title",
                    "property",
                    "task_time",
                    "job_type",
                    "apply_deadline",
                    "brokerage",
                    "asap",
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
        (_("Assignment"), {"fields": ("assigned_to", "is_verified")}),
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
                    "audio_file",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": (
                    "status",
                    "created_by",
                    "created_at",
                    "updated_at",
                    "not_acceptance_notification_sent",
                ),
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
            _("Other Details"),
            {
                "fields": (
                    "task_type",
                    "lockbox_code",
                    "instructions",
                    "include_sign",
                    "installation_or_remove_address",
                ),
            },
        ),
    )


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
                    "pickup_address",
                    "include_sign",
                ),
            },
        ),
    )


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
                    "vendor_notes",
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
