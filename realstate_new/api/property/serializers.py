from typing import Any

from rest_framework.serializers import BooleanField
from rest_framework.serializers import IntegerField

from realstate_new.master.models import LockBox
from realstate_new.master.models import Property
from realstate_new.utils.serializers import DynamicModelSerializer
from realstate_new.utils.serializers import TrackingModelSerializer


class LockBoxSerializer(DynamicModelSerializer):
    class Meta:
        model = LockBox
        fields = [
            "lockbox_type",
            "lockbox_code",
            "additional_info",
        ]


class PropertySerializer(TrackingModelSerializer):
    lockbox = LockBoxSerializer(required=False)
    delete = BooleanField(write_only=True, required=False)
    id = IntegerField(required=False)

    class Meta:
        model = Property
        fields = (
            "id",
            "city",
            "state",
            "zip",
            "street",
            "latitude",
            "longitude",
            "vacant",
            "pets",
            "concierge",
            "alarm_code",
            "gate_code",
            "lockbox",
            "delete",
        )

    def create(self, validated_data: Any) -> Any:
        lockbox = validated_data.pop("lockbox", None)
        if lockbox:
            lc_instance = LockBoxSerializer().create(validated_data=lockbox)

            validated_data["lockbox"] = lc_instance
        return super().create(validated_data)

    def update(self, instance: Any, validated_data: Any) -> Any:
        lockbox = validated_data.pop("lockbox", None)
        if lockbox:
            for k, v in lockbox.items():
                setattr(instance.lockbox, k, v)

            instance.lockbox.save(update_fields=list(lockbox.keys()))
        return super().update(instance, validated_data)
