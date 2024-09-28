from collections import OrderedDict
from itertools import chain
from operator import itemgetter
from typing import Any
from typing import Literal

from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
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

from .serializers import LatestTaskSerializer
from .serializers import LockBoxBSSerializer
from .serializers import LockBoxIRSerializer
from .serializers import OngoingTaskSerializer
from .serializers import OpenHouseTaskSerializer
from .serializers import ProfessionalTaskSerializer
from .serializers import RunnerTaskSerializer
from .serializers import ShowingTaskSerializer
from .serializers import SignTaskSerializer


class TaskListMixin:
    def get_updated_serializer(self, job):
        if job == "latest":
            return LatestTaskSerializer

        return OngoingTaskSerializer

    def get_tasks(
        self,
        request,
        base_query,
        job: Literal["completed", "ongoing", "latest"],
    ):
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

        serializer = self.get_updated_serializer(job=job)
        data = serializer(data, context={"request": request}).data
        flattened_response = chain.from_iterable(filter(bool, data.values()))
        return sorted(flattened_response, key=itemgetter("task_time"))

    def get_paginated_response(self, page, page_size, response: list):
        start = (page - 1) * page_size
        end = start + page_size
        return OrderedDict(
            [
                ("count", len(response)),
                ("page", page),
                ("page_size", page_size),
                ("results", response[start:end]),
            ],
        )


class TaskViewSet(ModelViewSet):
    def perform_create(self, serializer):
        amount = serializer.validated_data["payment_amount"]
        self.request.user.wallet.deduct_amount(amount)
        return super().perform_create(serializer)

    def get_serializer(self, *args: Any, **kwargs: Any) -> BaseSerializer:
        return super().get_serializer(
            *args,
            **kwargs,
            remove_fields=["application_status"],
        )


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
    queryset = SignTask.objects.all()


class OngoingTaskView(APIView, TaskListMixin):
    serializer_class = None

    @silk_profile(name="Ongoing Task")
    def get(self, request, *args, **kwargs):
        params = request.query_params
        base_query = {"is_completed": False, "created_by": request.user}
        page_size = int(params.get("page_size", 10))
        page = int(params.get("page", 1))
        tasks = self.get_tasks(request, base_query, "ongoing")
        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)


class CompletedTaskView(APIView, TaskListMixin):
    serializer_class = None

    @silk_profile(name="Completed Task")
    def get(self, request, *args, **kwargs):
        params = request.query_params
        base_query = {"is_completed": True, "created_by": request.user}
        page_size = int(params.get("page_size", 10))
        page = int(params.get("page", 1))
        tasks = self.get_tasks(request, base_query, "completed")
        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)


class LatestTaskView(APIView, TaskListMixin):
    @silk_profile(name="Latest Task")
    def get(self, request, *args, **kwargs):
        params = request.query_params
        base_query = {"is_completed": False, "assigned_to__isnull": True}
        page_size = int(params.get("page_size", 10))
        page = int(params.get("page", 1))
        tasks = self.get_tasks(request, base_query, "latest")
        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)
