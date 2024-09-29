from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        "id",
        "full_name",
        "email",
        "license_number",
        "license_status",
        "mile_radius_preference",
    ]
    list_filter = [
        "license_status",
        "license_jurisdiction",
        "job_preferences",
        "days_of_week_preferences",
    ]
    search_fields = [
        "license_number",
        "first_name",
        "last_name",
        "city",
        "state_province",
    ]

    custom_fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "mile_radius_preference",
                    "phone_country_code",
                    "phone",
                ),
            },
        ),
        (
            "Job Preferences",
            {
                "fields": (
                    "job_preferences",
                    "time_preference_start",
                    "time_preference_end",
                    "days_of_week_preferences",
                ),
            },
        ),
        (
            "License Information",
            {
                "fields": (
                    "license_number",
                    "license_issue_date",
                    "license_expiration_date",
                    "license_status",
                    "license_type",
                    "license_jurisdiction",
                ),
            },
        ),
        (
            "Address",
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "city",
                    "state_province",
                    "postal_code",
                    "country",
                ),
            },
        ),
    )

    fieldsets = UserAdmin.fieldsets + custom_fieldsets
