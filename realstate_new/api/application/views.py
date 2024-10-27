from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework.views import APIView

from realstate_new.api.user.serializers import UserSerializer
from realstate_new.application.models import JobApplication
from realstate_new.task.models import JOB_TYPE_MAPPINGS
from realstate_new.utils.pagination import CustomPageNumberPagination

from .serializers import JobApplicationSerializer


class JobApplicationCreateView(generics.ListCreateAPIView):
    serializer_class = JobApplicationSerializer
    queryset = JobApplication.objects.all().order_by("-created_at")


# class JobApplicationListView(generics.ListAPIView)


class AppliedUsersListView(APIView, CustomPageNumberPagination):
    serializer_class = UserSerializer

    def get(self, request, task_id, task_type, *args, **kwargs):
        model = JOB_TYPE_MAPPINGS[task_type]
        content_type = ContentType.objects.get_for_model(model=model)
        applicants = list(
            JobApplication.objects.filter(
                content_type=content_type,
                object_id=task_id,
            ).values_list(
                "applicant__id",
                flat=True,
            ),
        )
        qs = get_user_model().objects.filter(id__in=applicants)
        result_page = self.paginate_queryset(qs, request)
        serializer = self.serializer_class(
            result_page,
            many=True,
            context={"request": request},
            fields=(
                "id",
                "email",
                "license_number",
                "first_name",
                "last_name",
                "jobs_completed",
            ),
        )
        return self.get_paginated_response(serializer.data)
