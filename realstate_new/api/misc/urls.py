from django.urls import path

from .views import FeedbackView
from .views import ProfessionalInquiryView

urlpatterns = [
    path(
        "professional-inquiry/",
        ProfessionalInquiryView.as_view(),
    ),
    path(
        "feedback/",
        FeedbackView.as_view(),
    ),
]
