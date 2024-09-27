from django.urls import path

from .views import JobApplicationCreateView

urlpatterns = [
    path(
        "",
        JobApplicationCreateView.as_view(),
    ),
]
