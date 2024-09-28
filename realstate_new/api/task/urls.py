from django.urls import path
from rest_framework import routers

from .views import CompletedTaskView
from .views import LatestTaskView
from .views import LockBoxTaskBSViewSet
from .views import LockBoxTaskIRViewSet
from .views import OngoingTaskView
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
    path("ongoingtasks/", OngoingTaskView.as_view()),
    path("completedtasks/", CompletedTaskView.as_view()),
    path("latesttasks/", LatestTaskView.as_view()),
    *router.urls,
]
