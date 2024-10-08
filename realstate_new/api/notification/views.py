from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from realstate_new.notification.models import Notification

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
