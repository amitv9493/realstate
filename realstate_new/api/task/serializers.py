from utils.serializers import TrackingSerializer

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
    class Meta:
        model = ShowingTask
        fields = "__all__"


class LockBoxBSSerializer(TaskSerializer):
    class Meta:
        model = LockBoxTaskBS
        fields = "__all__"


class LockBoxIRSerializer(TaskSerializer):
    class Meta:
        model = LockBoxTaskIR
        fields = "__all__"


class OpenHouseTaskSerializer(TaskSerializer):
    class Meta:
        model = OpenHouseTask
        fields = "__all__"


class ProfessionalTaskSerializer(TaskSerializer):
    class Meta:
        model = ProfessionalServiceTask
        fields = "__all__"


class RunnerTaskSerializer(TaskSerializer):
    class Meta:
        model = RunnerTask
        fields = "__all__"


class SignTaskSerializer(TaskSerializer):
    class Meta:
        model = SignTask
        fields = "__all__"
