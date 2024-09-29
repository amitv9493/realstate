from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render


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
