from realstate_new.master.models import Property
from realstate_new.utils.serializers import TrackingModelSerializer


class PropertySerializer(TrackingModelSerializer):
    class Meta:
        model = Property
        fields = "__all__"
