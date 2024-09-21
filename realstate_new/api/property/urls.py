from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PropertyCreateView
from .views import PropertyViewSet

router = DefaultRouter()
router.register("", PropertyViewSet, basename="property")

urlpatterns = [
    path(
        "create/",
        PropertyCreateView.as_view(),
    ),
    *router.urls,
]
