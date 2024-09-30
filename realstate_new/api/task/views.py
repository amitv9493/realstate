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

from realstate_new.master.models.types import JOB_TYPE_MAPPINGS
from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models.professional_task import ProfessionalServiceTask
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


class TaskListMixin:
    def get_updated_serializer(self, job):
        return OngoingTaskSerializer

    def get_tasks(
        self,
        base_query,
        job: Literal["completed", "ongoing", "latest"],
    ):
        data = {}
        for k, job_model in JOB_TYPE_MAPPINGS.items():
            if job == "latest":
                # excluding those jobs where user has already made theh application
                data[k] = job_model.objects.filter(**base_query).exclude(
                    applications__applicant=self.request.user,
                )
            else:
                data[k] = job_model.objects.filter(**base_query)

        serializer = self.get_updated_serializer(job=job)
        data = serializer(data, context={"request": self.request}).data
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
    """Returns the list of the pending/ongoing tasks for the Job Creater."""

    serializer_class = None

    @silk_profile(name="Ongoing Task")
    def get(self, request, *args, **kwargs):
        params = request.query_params
        base_query = {"is_completed": False, "created_by": request.user}
        page_size = int(params.get("page_size", 10))
        page = int(params.get("page", 1))
        tasks = self.get_tasks(base_query, "ongoing")
        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)


class CompletedTaskView(APIView, TaskListMixin):
    """Returns the list of the completed tasks for the Job Creater."""

    serializer_class = None

    @silk_profile(name="Completed Task")
    def get(self, request, *args, **kwargs):
        params = request.query_params
        base_query = {"is_completed": True, "created_by": request.user}
        page_size = int(params.get("page_size", 10))
        page = int(params.get("page", 1))
        tasks = self.get_tasks(base_query, "completed")
        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)


class LatestTaskView(APIView, TaskListMixin):
    """Returns the list of the Available tasks for the Job Seeker.
    It does not include those tasks which the seeker has already applied to."""

    @silk_profile(name="Latest Task")
    def get(self, request, *args, **kwargs):
        params = request.query_params
        base_query = {"is_completed": False, "assigned_to__isnull": True}
        page_size = int(params.get("page_size", 10))
        page = int(params.get("page", 1))
        tasks = self.get_tasks(base_query, "latest")
        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)
