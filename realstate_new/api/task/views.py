from collections import OrderedDict
from itertools import chain
from operator import itemgetter

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from silk.profiling.profiler import silk_profile

from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models.professional_task import ProfessionalServiceTask
from realstate_new.task.models.runner_task import RunnerTask
from realstate_new.task.models.sign_task import SignTask
from realstate_new.users.models import User

from .serializers import LockBoxBSSerializer
from .serializers import LockBoxIRSerializer
from .serializers import OngoingTaskSerializer
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


class OngoingTaskView(APIView):
    serializer_class = None

    @silk_profile(name="ongoing task")
    def get(self, request, *args, **kwargs):
        page_size = int(request.query_params.get("page_size", 10))
        page = int(request.query_params.get("page", 1))
        start = (page - 1) * page_size
        end = start + page_size

        base_query = {"is_completed": False, "created_by": request.user}
        showing_tasks = ShowingTask.objects.filter(**base_query)
        sign_tasks = SignTask.objects.filter(**base_query)
        runner_tasks = RunnerTask.objects.filter(**base_query)
        professional_tasks = ProfessionalServiceTask.objects.filter(**base_query)
        openhouse_tasks = OpenHouseTask.objects.filter(**base_query)
        lockbox_tasks_bs = LockBoxTaskBS.objects.filter(**base_query)
        lockbox_tasks_ir = LockBoxTaskIR.objects.filter(**base_query)

        data = {
            "showing_tasks": showing_tasks,
            "sign_tasks": sign_tasks,
            "runner_tasks": runner_tasks,
            "professional_tasks": professional_tasks,
            "openhouse_tasks": openhouse_tasks,
            "lockbox_tasks_bs": lockbox_tasks_bs,
            "lockbox_tasks_ir": lockbox_tasks_ir,
        }

        data = OngoingTaskSerializer(data).data
        flattened_response = chain.from_iterable(filter(bool, data.values()))
        sorted_data = sorted(flattened_response, key=itemgetter("job_deadline"))

        data = OrderedDict(
            [
                ("count", len(sorted_data)),
                ("page", page),
                ("page_size", page_size),
                ("results", sorted_data[start:end]),
            ],
        )
        return Response(data, 200)


class CompletedTaskView(APIView):
    serializer_class = None

    @silk_profile(name="ongoing task")
    def get(self, request, *args, **kwargs):
        page_size = int(request.query_params.get("page_size", 10))
        page = int(request.query_params.get("page", 1))
        start = (page - 1) * page_size
        end = start + page_size

        base_query = {"is_completed": True, "created_by": request.user}
        showing_tasks = ShowingTask.objects.filter(**base_query)
        sign_tasks = SignTask.objects.filter(**base_query)
        runner_tasks = RunnerTask.objects.filter(**base_query)
        professional_tasks = ProfessionalServiceTask.objects.filter(**base_query)
        openhouse_tasks = OpenHouseTask.objects.filter(**base_query)
        lockbox_tasks_bs = LockBoxTaskBS.objects.filter(**base_query)
        lockbox_tasks_ir = LockBoxTaskIR.objects.filter(**base_query)

        data = {
            "showing_tasks": showing_tasks,
            "sign_tasks": sign_tasks,
            "runner_tasks": runner_tasks,
            "professional_tasks": professional_tasks,
            "openhouse_tasks": openhouse_tasks,
            "lockbox_tasks_bs": lockbox_tasks_bs,
            "lockbox_tasks_ir": lockbox_tasks_ir,
        }

        data = OngoingTaskSerializer(data).data
        flattened_response = chain.from_iterable(filter(bool, data.values()))
        sorted_data = sorted(flattened_response, key=itemgetter("job_deadline"))

        data = OrderedDict(
            [
                ("count", len(sorted_data)),
                ("page", page),
                ("page_size", page_size),
                ("results", sorted_data[start:end]),
            ],
        )
        return Response(data, 200)
