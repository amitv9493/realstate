from django.urls import path

from .views import AgentAssignedAddressView
from .views import ZipCodeDetailView

urlpatterns = [
    path("zipcode-detail", ZipCodeDetailView.as_view()),
    path("agent-assigned-address", AgentAssignedAddressView.as_view()),
]
