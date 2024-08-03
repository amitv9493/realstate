from django.urls import path

from .views import ArelloView

urlpatterns = [
    path("licenseinfo", ArelloView.as_view()),
]
