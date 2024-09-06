from rest_framework import routers

from .views import ShowingTaskViewSet

router = routers.SimpleRouter()
router.register("showingtask", ShowingTaskViewSet, "showing-task")

urlpatterns = [*router.urls]
