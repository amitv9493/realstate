from django.urls import path

from .views import UserView

urlpatterns = [
    path("update", UserView.as_view()),
]
