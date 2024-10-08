from realstate_new.notification.models import Notification
from realstate_new.utils.serializers import DynamicModelSerializer


class NotificationSerializer(DynamicModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "event",
            "description",
            "timestamp",
            "is_read",
        ]
        extra_kwargs = {"user": {"write_only": True}}
