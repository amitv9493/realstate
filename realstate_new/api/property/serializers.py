from typing import Any

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

    class Meta:
        model = Property
        fields = "__all__"

    def create(self, validated_data: Any) -> Any:
        lockbox = validated_data.pop("lockbox", None)
        if lockbox:
            lc_instance = LockBoxSerializer().create(validated_data=lockbox)

            validated_data["lockbox"] = lc_instance
        return super().create(validated_data)
