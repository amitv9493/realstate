from realstate_new.master.models import Property
from realstate_new.utils.serializers import DynamicModelSerializer


class PropertySerializer(DynamicModelSerializer):
    class Meta:
        model = Property
        fields = "__all__"
