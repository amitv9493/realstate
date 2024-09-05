from realstate_new.master.models import Property
from realstate_new.utils.serializers import TrackingSerializer


class PropertySerializer(TrackingSerializer):
    class Meta:
        model = Property
        fields = "__all__"
