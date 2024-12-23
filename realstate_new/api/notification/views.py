from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.viewsets import ModelViewSet

from realstate_new.notification.celery_tasks import celery_send_fcm_notification
from realstate_new.notification.models import Notification
from realstate_new.users.models import FCMDevice

from .serializers import NotificationSerializer


def hello(request):
    current_site = get_current_site(request)

    context = {
        "title": "Reset Password",
        "body": "Rest your password by clicking below.",
        "ButtonLink": "http://localhost:8000",
        "ButtonText": "Reset Password",
        "current_site": current_site.domain,
    }
    return render(request, "emails/base.html", context=context)


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    http_method_names = ["get", "patch"]

    def get_queryset(self):
        qs = super().get_queryset().order_by("-timestamp")
        user = self.request.user
        is_read = self.request.query_params.get("is_read", None)

        if is_read == "true":
            return qs.filter(user=user, is_read=True)
        return qs.filter(user=user, is_read=False) if is_read == "false" else qs.filter(user=user)


@csrf_exempt
def test_notification(request):
    ids = list(set(FCMDevice.objects.values_list("registration_id", flat=True)))
    celery_send_fcm_notification.delay(title="test", body="test", tokens=ids)
    return HttpResponse("done")
