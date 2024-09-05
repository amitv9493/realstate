from django.urls import path

from .views import UserMeView
from .views import UserView

urlpatterns = [
    path("update", UserView.as_view()),
    path("me", UserMeView.as_view()),
]
