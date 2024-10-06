from django.urls import path

from .views import AppliedUsersListView
from .views import JobApplicationCreateView

urlpatterns = [
    path(
        "",
        JobApplicationCreateView.as_view(),
    ),
    path(
        "userlist/<int:task_id>/<str:task_type>",
        AppliedUsersListView.as_view(),
    ),
]
