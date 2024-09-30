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
    *router.urls,
]
