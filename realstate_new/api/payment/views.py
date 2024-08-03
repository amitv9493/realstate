import logging

from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from paypalrestsdk import notifications

from realstate_new.payment.models import PayPalPayementHistory

__logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class ProcessWebhookView(View):
    def post(self, request):
        if "paypal-transmission-id" not in request.headers:
            return HttpResponseBadRequest()

        auth_algo = request.headers["paypal-auth-algo"]
        cert_url = request.headers["paypal-cert-url"]
        transmission_id = request.headers["paypal-transmission-id"]
        transmission_sig = request.headers["paypal-transmission-sig"]
        transmission_time = request.headers["paypal-transmission-time"]
        webhook_id = settings.PAYPAL_WEBHOOK_ID
        event_body = request.body.decode()
        valid = notifications.WebhookEvent.verify(
            transmission_id=transmission_id,
            timestamp=transmission_time,
            webhook_id=webhook_id,
            event_body=event_body,
            cert_url=cert_url,
            actual_sig=transmission_sig,
            auth_algo=auth_algo,
        )
        if not valid:
            PayPalPayementHistory.objects.create(
                transmission_id=transmission_id,
                # transmission_time =
                event_body=event_body,
                valid=valid,
            )
            msg = f"transcation with transmission id \
                {transmission_id} was unable to verify"
            __logger.critical(
                msg,
            )
            return HttpResponseBadRequest()

        return HttpResponse()
