from typing import Any

from utils.serializers import DynamicModelSerializer
from utils.serializers import TrackingSerializer

from realstate_new.task.models import LockBox
from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ProfessionalServiceTask
from realstate_new.task.models import RunnerTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models import SignTask


class TaskSerializer(TrackingSerializer):
    class Meta:
        extra_kwargs = {
            "created_by": {"read_only": True},
        }


class ShowingTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = ShowingTask
        fields = "__all__"


class LockBoxSerializer(DynamicModelSerializer):
    class Meta(TaskSerializer.Meta):
        model = LockBox
        fields = "__all__"
        exclude_fields = ["id", "lockbox_task"]


class LockBoxBSSerializer(TaskSerializer):
    lockbox = LockBoxSerializer()

    class Meta(TaskSerializer.Meta):
        model = LockBoxTaskBS
        fields = "__all__"

    def create(self, validated_data: Any) -> Any:
        lockbox_data = validated_data.pop("lockbox", None)
        lockbox_task = super().create(validated_data)
        if lockbox_data:
            LockBox.objects.create(**lockbox_data, lockbox_task=lockbox_task)
        return lockbox_task


class LockBoxIRSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = LockBoxTaskIR
        fields = "__all__"


class OpenHouseTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = OpenHouseTask
        fields = "__all__"


class ProfessionalTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = ProfessionalServiceTask
        fields = "__all__"


class RunnerTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = RunnerTask
        fields = "__all__"


class SignTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = SignTask
        fields = "__all__"
