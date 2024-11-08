from django.urls import path

from .views import ClientTokenView
from .views import StripeCreatePaymentIntentView
from .views import TestPayment
from .views import VerifiyPaymentView
from .views import webhook

urlpatterns = [
    path("token/", ClientTokenView.as_view()),
    path(
        "verify/",
        VerifiyPaymentView.as_view(),
    ),
    path(
        "test",
        TestPayment.as_view(),
    ),
    path(
        "create-payment",
        StripeCreatePaymentIntentView.as_view(),
    ),
    path(
        "webhook",
        webhook,
    ),
]
