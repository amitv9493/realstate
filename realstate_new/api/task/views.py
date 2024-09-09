from rest_framework.viewsets import ModelViewSet

from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models.professional_task import ProfessionalServiceTask
from realstate_new.users.models import User

from .serializers import LockBoxBSSerializer
from .serializers import LockBoxIRSerializer
from .serializers import OpenHouseTaskSerializer
from .serializers import ProfessionalTaskSerializer
from .serializers import RunnerTaskSerializer
from .serializers import ShowingTaskSerializer
from .serializers import SignTaskSerializer


class TaskViewSet(ModelViewSet):
    def perform_create(self, serializer):
        amount = serializer.validated_data["payment_amount"]
        self.request.user.wallet.deduct_amount(amount)
        return super().perform_create(serializer)


class ShowingTaskViewSet(TaskViewSet):
    serializer_class = ShowingTaskSerializer
    queryset = ShowingTask.objects.all()


def get_user_preferences(user: User):
    return user.days_of_week_preferences


class LockBoxTaskIRViewSet(TaskViewSet):
    serializer_class = LockBoxIRSerializer
    queryset = LockBoxTaskIR.objects.all()


class LockBoxTaskBSViewSet(TaskViewSet):
    serializer_class = LockBoxBSSerializer
    queryset = LockBoxTaskBS.objects.all()


class OpenHouseTaskViewSet(TaskViewSet):
    serializer_class = OpenHouseTaskSerializer
    queryset = OpenHouseTask.objects.all()


class ProfessionalTaskViewSet(TaskViewSet):
    serializer_class = ProfessionalTaskSerializer
    queryset = ProfessionalServiceTask.objects.all()


class RunnerTaskViewSet(TaskViewSet):
    serializer_class = RunnerTaskSerializer
    queryset = ProfessionalServiceTask.objects.all()


class SignTaskViewSet(TaskViewSet):
    serializer_class = SignTaskSerializer
    queryset = ProfessionalServiceTask.objects.all()
