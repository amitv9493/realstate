from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProfessionalDetailViewSet
from .views import UserMeView
from .views import UserView

router = DefaultRouter()

router.register("professional-detail", ProfessionalDetailViewSet)
urlpatterns = [
    path("update", UserView.as_view()),
    path("me", UserMeView.as_view()),
    *router.urls,
]
