from rest_framework import routers

from .views import TaskViewSet

router = routers.SimpleRouter()
router.register("showingtask", TaskViewSet, "showing-task")

urlpatterns = [*router.urls]
