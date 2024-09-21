from datetime import datetime

from rest_framework import serializers

from realstate_new.master.models import Property
from realstate_new.master.models import PropertyStatus
from realstate_new.utils.serializers import TrackingModelSerializer
from realstate_new.utils.serializers import TrackingSerializer


class PropertySerializer(TrackingModelSerializer):
    class Meta:
        model = Property
        fields = "__all__"


class PropertyCreateSerializer(TrackingSerializer):
    address = serializers.JSONField()
    coordinates = serializers.JSONField()
    list_price = serializers.IntegerField()
    listing_date = serializers.IntegerField()
    listing_type = serializers.CharField()
    lot_size = serializers.JSONField()
    status = serializers.CharField()
    size = serializers.IntegerField()
    year_built = serializers.IntegerField()
    system_id = serializers.IntegerField()
    description = serializers.CharField()

    def create(self, validated_data):
        data = validated_data
        self.set_created_by(validated_data)
        listing_date = datetime.fromtimestamp(int(data["listing_date"]))  # noqa: DTZ006
        status = PropertyStatus.AVAILABLE if data["status"] == "Active" else PropertyStatus.OTHER
        return Property.objects.get_or_create(
            delivery_line=data["address"]["delivery_line"],
            city=data["address"]["city"],
            state=data["address"]["state"],
            zip=data["address"]["zip"],
            street=data["address"]["street"],
            latitude=data["coordinates"]["latitude"],
            longitude=data["coordinates"]["longitude"],
            price=data["list_price"],
            # listing_type
            listing_date=listing_date,
            status=status,
            lotsize_sqft=data["lot_size"]["sqft"],
            lotsize_acres=data["lot_size"]["acres"],
            size=data["size"],
            year_built=data["year_built"],
            mls_number=data["system_id"],
            description=data["description"],
            created_by=data["created_by"],
        )
