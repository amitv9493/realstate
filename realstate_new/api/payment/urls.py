from django.urls import path

from .views import CreatePaymentView
from .views import ExecutePaymentView

urlpatterns = [
    path("paypal/order/create", CreatePaymentView.as_view()),
    path("paypal/order/confirm", ExecutePaymentView.as_view()),
]
