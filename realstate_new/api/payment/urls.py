from django.urls import path

from .views import AccountStatusView
from .views import ClientTokenView
from .views import ConnectAccountCreateView
from .views import StripeCreatePaymentIntentView
from .views import TestPayment
from .views import VerifiyPaymentView
from .views import account_update_webhook
from .views import get_refresh_link
from .views import get_return_link
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
        "stripe/create/paymentintent",
        StripeCreatePaymentIntentView.as_view(),
    ),
    path(
        "stripe/intent/webhook",
        webhook,
    ),
    path(
        "stripe/account-update/webhook",
        account_update_webhook,
    ),
    path(
        "stripe/create-account",
        ConnectAccountCreateView.as_view(),
        name="create-account",
    ),
    path(
        "stripe/refresh/<str:account_id>",
        get_refresh_link,
        name="refresh-link",
    ),
    path(
        "stripe/return/<str:account_id>",
        get_return_link,
        name="return-link",
    ),
    path(
        "stripe/account/status",
        AccountStatusView.as_view(),
        name="account-status",
    ),
]
