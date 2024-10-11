from collections import OrderedDict
from itertools import chain
from typing import Any

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from silk.profiling.profiler import silk_profile

from realstate_new.master.models.types import JOB_TYPE_MAPPINGS
from realstate_new.notification.models import Notification
from realstate_new.notification.models import NotificationChoices
from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ProfessionalServiceTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models import SignTask
from realstate_new.task.models.choices import TaskStatusChoices
from realstate_new.users.models import User

from .filters import filter_tasks
from .serializers import LockBoxBSSerializer
from .serializers import LockBoxIRSerializer
from .serializers import OngoingTaskSerializer
from .serializers import OpenHouseTaskSerializer
from .serializers import ProfessionalTaskSerializer
from .serializers import RunnerTaskSerializer
from .serializers import ShowingTaskSerializer
from .serializers import SignTaskSerializer
from .serializers import TaskActionSerializer


class TaskListMixin:
    def get_updated_serializer(self):
        return OngoingTaskSerializer

    def get_tasks(
        self,
        base_query,
    ):
        filter_data = self.get_filtered_qs(base_query)
        serialized_data = self.serialize_data(filter_data)

        return self.apply_sorting(flattened_response=serialized_data)

    def get_filtered_qs(self, base_query):
        data = {}
        filtered_tasks = filter_tasks(self.request, base_query)
        for task_type, task_filter in filtered_tasks.items():
            data[task_type] = task_filter.qs
        return data

    def serialize_data(self, data):
        serializer = self.get_updated_serializer()
        data = serializer(data, context={"request": self.request}).data
        return chain.from_iterable(filter(bool, data.values()))

    def apply_sorting(self, flattened_response):
        sort_by = self.request.query_params.get("sort_by", "task_time")
        sort_order = self.request.query_params.get("sort_order", "asc")

        if sort_order == "desc":
            return sorted(
                flattened_response,
                key=lambda x: x.get(sort_by, ""),
                reverse=True,
            )
        return sorted(flattened_response, key=lambda x: x.get(sort_by, ""))

    def get_paginated_response(self, page: int, page_size: int, response: list):
        start = (page - 1) * page_size
        end = start + page_size
        return OrderedDict(
            [
                ("count", len(response) if response else 0),
                ("page", page if response else 0),
                ("page_size", page_size if response else 0),
                ("results", response[start:end] if response else []),
            ],
        )


class JobCreaterDashboardView(APIView, TaskListMixin):
    """Returns the list of the pending/ongoing tasks for the Job Creater."""

    serializer_class = None

    @silk_profile(name="Ongoing Task")
    def get(self, request, *args, **kwargs):
        params = request.query_params
        flag = params.get("flag", "").lower()
        if not flag:
            raise ValidationError(
                {
                    "flag": "flag is required",
                },
                code="required",
            )
        base_query = Q(created_by=request.user)
        if flag == "ongoing":
            base_query &= Q(is_verified=False)

        if flag == "completed":
            base_query &= Q(is_verified=True)

        tasks = self.get_tasks(base_query)

        # pagination related data
        page_size = params.get("page_size", 10)
        page = params.get("page", 1)
        page_size = int(page_size) if page_size else 10
        page = int(page) if page else 1

        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)


class JobSeekerDashboardView(APIView, TaskListMixin):
    @silk_profile(name="Latest Task")
    def get(self, request, *args, **kwargs):
        params = request.query_params
        page_size = params.get("page_size", 10)
        page = params.get("page", 1)

        page_size = int(page_size) if page_size else 10
        page = int(page) if page else 1
        flag = params.get("flag", "").lower()
        if not flag:
            raise ValidationError(
                {
                    "flag": "Flag is required",
                },
                code="required",
            )
        if flag == "latest":
            query = (
                Q(is_verified=False)
                & Q(assigned_to__isnull=True)
                & ~Q(
                    applications__applicant__in=[request.user],
                )
            )
        if flag == "appliedjobs":
            query = Q(assigned_to=request.user)

        tasks = self.get_tasks(query)
        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)


class TaskViewSet(ModelViewSet):
    def get_serializer(self, *args: Any, **kwargs: Any) -> BaseSerializer:
        return super().get_serializer(
            *args,
            **kwargs,
            remove_fields=["application_status"],
        )

    def perform_create(self, serializer) -> None:
        instance = serializer.save()
        Notification.objects.create(
            event=TaskStatusChoices.CREATED,
            content_object=instance,
            user=self.request.user,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        Notification.objects.create_notifications(
            task=instance,
            event=NotificationChoices.DETAILS_UPDATED,
            users=[instance.created_by, instance.assigned_to],
        )

        return super().perform_update(serializer)


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


class TaskActionView(APIView):
    serializer_class = TaskActionSerializer

    def post(self, request, task_type, task_id, task_action, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            task_model = JOB_TYPE_MAPPINGS[task_type]
            task_instance = task_model.objects.get(id=task_id)
            task_action = getattr(NotificationChoices, task_action.upper())

            if task_action == TaskStatusChoices.ASSIGNED:
                task_instance.assigned_to = data["assigned_to"]
                task_instance.save(update_fields=["assigned_to"])
                Notification.objects.create_notifications(
                    task_instance,
                    event=task_action,
                    users=[task_instance.assigned_to, task_instance.created_by],
                )

            if task_action == TaskStatusChoices.REASSIGNED:
                task_instance.assigned_to = data["assigned_to"]
                task_instance.save(update_fields=["assigned_to"])
                Notification.objects.create_notifications(
                    task_instance,
                    event=task_action,
                    users=[task_instance.assigned_to, task_instance.created_by],
                )
            if task_action == TaskStatusChoices.MARK_COMPLETED:
                task_instance.marked_completed_by_assignee = True
                task_instance.save(update_fields=["marked_completed_by_assignee"])
                Notification.objects.create_notifications(
                    task_instance,
                    event=task_action,
                    users=[task_instance.assigned_to, task_instance.created_by],
                )
            if task_action == TaskStatusChoices.COMPLETED:
                task_instance.is_verified = True
                task_instance.save(update_fields=["is_verified"])
                Notification.objects.create_notifications(
                    task_instance,
                    event=task_action,
                    users=[task_instance.assigned_to, task_instance.created_by],
                )

            if task_action == TaskStatusChoices.CREATER_CANCELLED:
                task_instance.is_cancelled = True
                task_instance.save(update_fields=["is_cancelled"])
                users = [task_instance.created_by]
                if u := task_instance.assigned_to:
                    users.append(u)

                Notification.objects.create_notifications(
                    task_instance,
                    event=task_action,
                    users=users,
                )
            if task_action == TaskStatusChoices.ASSIGNER_CANCELLED:
                task_instance.assigned_to = None
                task_instance.save(update_fields=["assigned_to"])

                Notification.objects.create_notifications(
                    task_instance,
                    event=task_action,
                    users=[task_instance.assigned_to, task_instance.created_by],
                )
        return Response({"status": True}, 200)
