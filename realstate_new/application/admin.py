from django.contrib import admin

from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "content_type",
        "object_id",
        "status",
        "applicant",
        "created_at",
    )
    list_filter = ("content_type", "applicant", "created_at")
    date_hierarchy = "created_at"
