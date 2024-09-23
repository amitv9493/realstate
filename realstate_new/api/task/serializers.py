from typing import Any

from rest_framework import serializers

from realstate_new.task.models import LockBox
from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ProfessionalServiceTask
from realstate_new.task.models import RunnerTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models import SignTask
from realstate_new.utils.serializers import TrackingModelSerializer

ONGOING_FIELDS = (
    "id",
    "title",
    "created-at",
    "task_time",
    "payment_amount",
    "job_deadline",
    "apply_deadline",
    "created_by",
    "assigned_to",
    "property",
    "type_of_task",
)


class TaskSerializer(TrackingModelSerializer):
    type_of_task = serializers.CharField(read_only=True)

    class Meta:
        extra_kwargs = {
            "created_by": {"read_only": True},
        }


class ShowingTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = ShowingTask
        fields = "__all__"


class LockBoxSerializer(TaskSerializer):
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


class OngoingTaskSerializer(serializers.Serializer):
    showing_tasks = ShowingTaskSerializer(many=True, fields=ONGOING_FIELDS)
    sign_tasks = SignTaskSerializer(many=True, fields=ONGOING_FIELDS)
    runner_tasks = RunnerTaskSerializer(many=True, fields=ONGOING_FIELDS)
    professional_tasks = ProfessionalTaskSerializer(many=True, fields=ONGOING_FIELDS)
    openhouse_tasks = OpenHouseTaskSerializer(many=True, fields=ONGOING_FIELDS)
    lockbox_tasks_bs = LockBoxBSSerializer(many=True, fields=ONGOING_FIELDS)
    lockbox_tasks_ir = LockBoxIRSerializer(many=True, fields=ONGOING_FIELDS)
