from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

app_name = "api"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

urlpatterns = [
    path("auth/", include("realstate_new.api.auth.urls")),
    path("task/", include("realstate_new.api.task.urls")),
    path("user/", include("realstate_new.api.user.urls")),
    path("property/", include("realstate_new.api.property.urls")),
    path("payment/", include("realstate_new.api.payment.urls")),
    path("application/", include("realstate_new.api.application.urls")),
    path("arello/", include("realstate_new.api.third_party_apis.arello.urls")),
    path("slipstream/", include("realstate_new.api.third_party_apis.slipstream.urls")),
    path("notification/", include("realstate_new.api.notification.urls")),
    path("misc/", include("realstate_new.api.misc.urls")),
    *router.urls,
]
