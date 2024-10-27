from django.urls import path

from .views import ClientTokenView
from .views import VerifiyPaymentView

urlpatterns = [
    path("token/", ClientTokenView.as_view()),
    path(
        "verify/",
        VerifiyPaymentView.as_view(),
    ),
]
