from collections import OrderedDict
from itertools import chain
from typing import Any

import stripe
from django.db.models import Prefetch
from django.db.models import Q
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from realstate_new.master.models.property import Property
from realstate_new.notification.models import Notification
from realstate_new.notification.models import NotificationChoices
from realstate_new.payment.models.stripe import StripeTranscation
from realstate_new.payment.models.stripe import TranscationStatus
from realstate_new.payment.models.stripe import TxnType
from realstate_new.task.models import JOB_TYPE_MAPPINGS
from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ProfessionalServiceTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models import SignTask
from realstate_new.task.models import VerificationDocument
from realstate_new.task.models.basetask import BaseTask
from realstate_new.task.models.choices import TaskStatusChoices
from realstate_new.task.models.open_for_vendor_task import OpenForVendorTask
from realstate_new.task.models.open_for_vendor_task import VendorType
from realstate_new.task.models.runner_task import RunnerTask
from realstate_new.users.models import User
from realstate_new.utils.permissions import AssigneeObjectPermission

from .filters import filter_tasks
from .serializers import LockBoxBSSerializer
from .serializers import LockBoxIRSerializer
from .serializers import OngoingTaskSerializer
from .serializers import OpenForVendorTaskSerializer
from .serializers import OpenHouseTaskSerializer
from .serializers import ProfessionalTaskSerializer
from .serializers import RunnerTaskSerializer
from .serializers import ShowingTaskSerializer
from .serializers import SignTaskSerializer
from .serializers import TaskActionSerializer
from .serializers import VendorTypeSerializer
from .serializers import VerificationDocumentSerializer


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

    def get(self, request, *args, **kwargs):
        params_list = ["completed", "created", "ongoing", "payment-pending"]
        params = request.query_params
        flag = params.get("flag", "").lower()
        if not flag:
            raise ValidationError(
                {
                    "flag": "flag is required",
                },
                code="required",
            )
        if flag not in params_list:
            raise ValidationError(
                {
                    "flag": "flag is invallid",
                },
            )
        base_query = Q(created_by=request.user)
        if flag == "ongoing":
            base_query &= Q(
                is_verified=False,
                assigned_to__isnull=False,
                payment_verified=True,
            )

        if flag == "completed":
            base_query &= Q(is_verified=True)

        if flag == "created":
            base_query &= Q(status=TaskStatusChoices.CREATED, assigned_to__isnull=True)
        if flag == "payment-pending":
            base_query &= Q(
                status=TaskStatusChoices.CREATED,
                assigned_to__isnull=True,
                payment_verified=False,
            )

        tasks = self.get_tasks(base_query)

        # pagination related data
        page_size = params.get("page_size", 10)
        page = params.get("page", 1)
        page_size = int(page_size) if page_size else 10
        page = int(page) if page else 1

        paginated_response = self.get_paginated_response(page, page_size, tasks)

        return Response(paginated_response, 200)


class JobSeekerDashboardView(APIView, TaskListMixin):
    def get(self, request, *args, **kwargs):
        params = request.query_params
        query_params_list = ["ongoing", "latest", "applied", "completed"]
        # pagination
        page = params.get("page", 1)
        page = int(page) if page else 1
        page_size = params.get("page_size", 10)
        page_size = int(page_size) if page_size else 10
        flag = params.get("flag", "").lower()

        if not flag:
            raise ValidationError(
                {
                    "flag": "Flag is required",
                },
                code="required",
            )
        if flag not in query_params_list:
            raise ValidationError(
                {
                    "flag": "Invalid Flag",
                },
                code="BadRequest",
            )
        if flag == "latest":
            query = (
                Q(status=TaskStatusChoices.CREATED)
                & Q(assigned_to__isnull=True)
                & ~Q(
                    applications__applicant__in=[request.user],
                )
                & ~Q(created_by=request.user)
                & Q(payment_verified=True)
            )
        if flag == "applied":
            query = Q(applications__applicant__in=[request.user]) & Q(
                status__in=[TaskStatusChoices.CREATED],
            )

        if flag == "ongoing":
            query = Q(
                assigned_to=request.user,
                status__in=[
                    TaskStatusChoices.ASSIGNED,
                    TaskStatusChoices.STARTED,
                    TaskStatusChoices.REASSIGNED,
                ],
            )
        if flag == "completed":
            query = Q(assigned_to=request.user) & Q(
                status__in=[
                    TaskStatusChoices.MARK_COMPLETED,
                    TaskStatusChoices.VERIFIED,
                ],
            )

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

    def perform_update(self, serializer):
        file_exists = serializer.instance.audio_file
        instance = serializer.instance
        if file_exists:
            Notification.objects.create_notifications(
                task=instance,
                event=NotificationChoices.DETAILS_UPDATED,
                users=[instance.created_by, instance.assigned_to],
            )

        return super().perform_update(serializer)


class ShowingTaskViewSet(TaskViewSet):
    serializer_class = ShowingTaskSerializer
    queryset = (
        ShowingTask.objects.select_related("assigned_to", "created_by")
        .prefetch_related(
            Prefetch(
                "property_address",
                queryset=Property.objects.select_related("lockbox"),
            ),
        )
        .all()
    )


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
    queryset = RunnerTask.objects.all()


class SignTaskViewSet(TaskViewSet):
    serializer_class = SignTaskSerializer
    queryset = SignTask.objects.all()


class OpenForVendorTaskViewSet(TaskViewSet):
    serializer_class = OpenForVendorTaskSerializer
    queryset = OpenForVendorTask.objects.all()


class OpenForVendorTypeView(ListCreateAPIView):
    queryset = VendorType.objects.all()
    serializer_class = VendorTypeSerializer


class TaskActionView(APIView):
    serializer_class = TaskActionSerializer
    permission_classes = [AssigneeObjectPermission]

    def post(self, request, task_type, task_id, task_action, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"task_action": task_action},
        )

        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            task_action = getattr(TaskStatusChoices, task_action.upper())
            request.task_action = task_action
            data = serializer.validated_data
            task_instance = self.get_object(task_id, task_type)

            action_handler = self.get_action_handler(task_action)
            action_handler(task_instance, data)

            return Response({"status": True}, 200)

    def get_object(self, task_id, task_type):
        try:
            model = JOB_TYPE_MAPPINGS[task_type]
            task_instance = model.objects.get(id=task_id)
            self.check_object_permissions(self.request, task_instance)
        except model.DoesNotExist as e:
            msg = "task does not exists"
            raise ValidationError(msg) from e
        else:
            return task_instance

    def get_action_handler(self, task_action):
        """Map task action to the appropriate handler method."""
        return {
            TaskStatusChoices.ASSIGNED: self.handle_assigned,
            TaskStatusChoices.STARTED: self.handle_started,
            TaskStatusChoices.VERIFIED: self.handle_verify,
            TaskStatusChoices.CREATER_CANCELLED: self.handle_creater_cancelled,
            TaskStatusChoices.ASSIGNER_CANCELLED: self.handle_assigner_cancelled,
            TaskStatusChoices.REASSIGNED: self.handle_reassigned,
            TaskStatusChoices.MARK_COMPLETED: self.handle_mark_completed,
        }.get(task_action)

    def handle_started(self, task_instance, validated_data):
        self.is_job_assigned(task_instance)
        self.create_notifications(
            task_instance,
            event=TaskStatusChoices.STARTED,
        )

    def handle_assigned(self, task_instance, validated_data):
        if task_instance.assigned_to:
            msg = "task has already been assigned."
            raise ValidationError(msg)

        task_instance.assigned_to = validated_data["assigned_to"]
        task_instance.save(update_fields=["assigned_to"])
        self.create_notifications(
            task_instance,
            event=TaskStatusChoices.ASSIGNED,
        )

    def handle_reassigned(self, task_instance, validated_data):
        # TODO:
        # remove this in future. This is superfulous
        task_instance.assigned_to = validated_data["assigned_to"]
        task_instance.save(update_fields=["assigned_to"])
        self.create_notifications(
            task_instance,
            event=TaskStatusChoices.REASSIGNED,
        )

    def handle_mark_completed(self, task_instance, validated_data):
        self.is_job_assigned(task_instance)
        task_instance.marked_completed_by_assignee = True
        images = validated_data["image_list"]
        image_objects = [
            VerificationDocument(content_object=task_instance, image=image) for image in images
        ]
        VerificationDocument.objects.bulk_create(image_objects)
        task_instance.save(update_fields=["marked_completed_by_assignee"])
        self.create_notifications(
            task_instance,
            event=TaskStatusChoices.MARK_COMPLETED,
        )

    def handle_verify(self, task_instance: BaseTask, validated_data):
        self.is_job_assigned(task_instance)

        if not task_instance.is_verified:
            task_instance.is_verified = True
            task_instance.save(update_fields=["is_verified"])
            transfer = stripe.Transfer.create(
                amount=int(task_instance.payment_amt_for_payout * 100),
                currency="usd",
                destination=task_instance.assigned_to.stripe_account_id,
            )
            StripeTranscation.objects.create(
                user=task_instance.assigned_to,
                amt=task_instance.payment_amt_for_payout,
                status=TranscationStatus.SUCCESS,
                txn_type=TxnType.PAYOUT,
                identifier=transfer.id,
                content_object=task_instance,
            )

            self.create_notifications(task_instance, event=TaskStatusChoices.VERIFIED)

    def handle_creater_cancelled(self, task_instance, validated_data):
        task_instance.is_cancelled = True
        task_instance.save(update_fields=["is_cancelled"])
        users = [task_instance.created_by]
        if u := task_instance.assigned_to:
            users.append(u)

        self.create_notifications(
            task_instance,
            event=TaskStatusChoices.CREATER_CANCELLED,
            users=users,
        )

    def handle_assigner_cancelled(self, task_instance, validated_data):
        self.is_job_assigned(task_instance)
        self.create_notifications(
            task_instance,
            event=TaskStatusChoices.ASSIGNER_CANCELLED,
        )
        task_instance.assigned_to = None
        task_instance.save(update_fields=["assigned_to"])

    def create_notifications(self, task_instance, event, users: list | None = None):
        if not users:
            users = [task_instance.assigned_to, task_instance.created_by]
        Notification.objects.create_notifications(
            task_instance,
            event=event,
            users=users,
        )

    def is_job_assigned(self, task_instance):
        """Check if the job  has assignee.

        Args:
            task_instance (BaseTask): Any task model created inherting the BaseTask.

        Raises:
            ValidationError: _description_

        Returns:
            bool: returns True if assigned else raise validation error.
        """
        if not task_instance.assigned_to:
            msg = "Job has no assignee"
            raise ValidationError(msg)
        return True


class TaskVerificationImageView(APIView):
    def get(self, request, task_type, task_id, *args, **kwargs):
        try:
            task_instance = JOB_TYPE_MAPPINGS[task_type].objects.get(id=task_id)
        except Exception:  # noqa: BLE001
            return Response({"error": "invalid task or task_id"}, 400)
        data = VerificationDocumentSerializer(
            task_instance.verification_images.all(),
            many=True,
        ).data
        return Response(data, 200)
