from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProfessionalDetailViewSet
from .views import TestNotification
from .views import UserMeView
from .views import UserView
from .views import test_logs

router = DefaultRouter()

router.register("professional-detail", ProfessionalDetailViewSet)
urlpatterns = [
    path("update", UserView.as_view()),
    path("me", UserMeView.as_view()),
    path("notify", TestNotification.as_view()),
    path(
        "test-logs",
        test_logs,
    ),
    *router.urls,
]
