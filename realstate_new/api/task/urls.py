from django.urls import path
from rest_framework import routers

from .views import JobCreaterDashboardView
from .views import JobSeekerDashboardView
from .views import LockBoxTaskBSViewSet
from .views import LockBoxTaskIRViewSet
from .views import OpenHouseTaskViewSet
from .views import ProfessionalTaskViewSet
from .views import RunnerTaskViewSet
from .views import ShowingTaskViewSet
from .views import SignTaskViewSet
from .views import TaskActionView
from .views import TaskVerificationImageView

router = routers.SimpleRouter()
router.register("showingtask", ShowingTaskViewSet, "showing-task")
router.register("lockboxtaskbs", LockBoxTaskBSViewSet, "lockboxbs-task")
router.register("lockboxtaskir", LockBoxTaskIRViewSet, "lockboxir-task")
router.register("openhouse", OpenHouseTaskViewSet, "openhouse-task")
router.register("professionalservicetask", ProfessionalTaskViewSet, "professional-task")
router.register("runnertask", RunnerTaskViewSet, "runner-task")
router.register("signtask", SignTaskViewSet, "sign-task")


urlpatterns = [
    path("dashboard/jobcreater", JobCreaterDashboardView.as_view()),
    path("dashboard/jobseeker", JobSeekerDashboardView.as_view()),
    path(
        "<str:task_type>/<int:task_id>/<str:task_action>",
        TaskActionView.as_view(),
    ),
    path(
        "<str:task_type>/<int:task_id>/verificationdocs/",
        TaskVerificationImageView.as_view(),
    ),
    *router.urls,
]
