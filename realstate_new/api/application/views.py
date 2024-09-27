from rest_framework import generics

from realstate_new.application.models import JobApplication

from .serializers import JobApplicationSerializer


class JobApplicationCreateView(generics.ListCreateAPIView):
    serializer_class = JobApplicationSerializer
    queryset = JobApplication.objects.all().order_by("-created_at")


# class JobApplicationListView(generics.ListAPIView)
