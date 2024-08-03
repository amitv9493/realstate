from django.urls import path

from .views import ProcessWebhookView

urlpatterns = [path("callback", ProcessWebhookView.as_view())]
