from django.contrib import admin

from .models import Property
from .models import PropertyFeature


@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ("id", "feature_name")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "property_address",
        "property_type",
        "listing_date",
        "Status",
        "price",
        "bedrooms",
        "bathrooms",
        "lot_size",
        "square_footage",
        "year_built",
        "mls_number",
        "description",
    )
    list_filter = ("created_at", "updated_at", "created_by", "listing_date")
    raw_id_fields = ("features",)
    date_hierarchy = "created_at"
