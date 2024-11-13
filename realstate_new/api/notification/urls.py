from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet
from .views import test_notification

router = DefaultRouter()
router.register("", NotificationViewSet, basename="notification")
urlpatterns = [path("test", test_notification, name="test-notification"), *router.urls]
