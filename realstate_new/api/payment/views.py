import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from realstate_new.payment.models import StripeTranscation
from realstate_new.payment.models import Transcation
from realstate_new.payment.models import TranscationStatus
from realstate_new.payment.models import TxnType
from realstate_new.payment.models.choices import PaymentStatusChoices
from realstate_new.task.models import JOB_TYPE_MAPPINGS
from realstate_new.task.models import get_job

from .hyperwallet import HyperwalletPayoutHandler
from .serializers import PaymentVerificationSerializer

_logger = logging.getLogger(__name__)
gateway = settings.BRAINTREE_GATEWAY


class ClientTokenView(APIView):
    """
    Args:
        APIView (_type_): Generate a client token which frontend uses to make payment
    """

    def get(self, request, *args, **kwargs):
        client_token = gateway.client_token.generate()
        return Response({"token": client_token}, 200)


class VerifiyPaymentView(APIView):
    serializer_class = PaymentVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = PaymentVerificationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            data = serializer.validated_data
            nonce = data.get("nonce", None)
            amt = data.get("amt", None)
            task_type = data.get("task_type", None)
            task_id = data.get("task_id", None)
            task = get_job(task_type, id=task_id)
            txn = Transcation.objects.create(
                user=request.user,
                status=PaymentStatusChoices.INITIATED,
                nonce=nonce,
                content_object=task,
            )
            try:
                result = gateway.transaction.sale(
                    {
                        "amount": amt,
                        "payment_method_nonce": nonce,
                        "options": {
                            "submit_for_settlement": True,
                            "three_d_secure": {"required": False},
                        },
                    },
                )

                if result.is_success:
                    self.payment_success(task, txn, result.transaction.id)
                    return Response(
                        {
                            "success": True,
                            "transaction_id": result.transaction.id,
                            "message": "Payment processed successfully",
                        },
                    )
                if result.transaction:
                    self.payment_failed(task, txn)
                    return Response(
                        {
                            "success": False,
                            "error": {
                                "code": result.transaction.processor_response_code,
                                "text": result.transaction.processor_response_text,
                            },
                        },
                    )
                errors = [
                    {
                        "attribute": error.attribute,
                        "code": error.code,
                        "message": error.message,
                    }
                    for error in result.errors.deep_errors
                ]

                return Response({"success": False, "errors": errors})

            except Exception as e:  # noqa: BLE001
                self.payment_failed(task, txn)
                return Response({"success": False, "error": str(e)}, status=500)

    def payment_success(self, task, txn, txn_id):
        txn.txn_id = txn_id
        task.payment_verified = True
        txn.status = PaymentStatusChoices.SUCCESS
        task.save(update_fields=["payment_verified"])
        txn.save(update_fields=["status", "txn_id"])

    def payment_failed(self, task, txn):
        task.payment_verified = False
        txn.status = PaymentStatusChoices.FAILURE
        task.save(update_fields=["payment_verified"])
        txn.save(update_fields=["status"])


class TestPayment(APIView):
    def post(self, request, *args, **kwargs):
        handler = HyperwalletPayoutHandler()
        task = get_job("Showing", 7)
        response = handler.create_payment(task, 100.00)
        return Response(response)


class StripeCreatePaymentIntentView(APIView):
    class PaymentSerialier(serializers.Serializer):
        amt = serializers.IntegerField()
        task_id = serializers.IntegerField()
        task_type = serializers.ChoiceField(choices=list(JOB_TYPE_MAPPINGS.keys()))
        payment_method_id = serializers.CharField(max_length=255, required=False)
        should_save_payment_method = serializers.BooleanField(
            required=False,
            default=False,
        )

    serializer_class = PaymentSerialier

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            data = serializer.validated_data
            task = get_job(data["task_type"], data["task_id"])
            try:
                intent_id, client_secret = self.create_intent_simple(
                    serialized_data=data,
                )
            except Exception as e:  # noqa: BLE001
                return Response({"error": str(e)}, 400)
            else:
                StripeTranscation.objects.create(
                    user=request.user,
                    amt=data["amt"],
                    status=TranscationStatus.INITIATED,
                    txn_type=TxnType.PAYIN,
                    identifier=intent_id,
                    content_object=task,
                )
                return Response(client_secret, 200)

    def create_intent_simple(self, serialized_data):
        data = serialized_data
        params = {
            "amount": data["amt"],
            "currency": "usd",
            "automatic_payment_methods": {
                "enabled": True,
            },
        }
        if data["should_save_payment_method"]:
            params["setup_future_usage"] = "off_session"
        intent = stripe.PaymentIntent.create(**params)
        return (
            intent.id,
            intent.client_secret,
        )

    def create_intent_advance(self, serialized_data):
        try:
            data = serialized_data
            params = {
                "amount": data["amt"],
                "currency": "usd",
                "automatic_payment_methods": {
                    "enabled": True,
                },
                "confirm": True,
                # the PaymentMethod ID sent by your client
                "payment_method": data["payment_method_id"],
                # Set this to "stripesdk://payment_return_url/" + your application ID
                "return_url": "stripesdk://payment_return_url/com.company.myapp",
                "mandate_data": {
                    "customer_acceptance": {
                        "type": "online",
                        "online": {
                            "ip_address": self.request.META.get("REMOTE_ADDR", ""),
                            "user_agent": self.request.headers.get("user-agent", ""),
                        },
                    },
                },
            }
            if data["should_save_payment_method"]:
                params["setup_future_usage"] = (
                    "off_session"  # Set setup_future_usage if should_save_payment_method is true
                )
            intent = stripe.PaymentIntent.create(**params)
            return Response({"client_secret": intent.client_secret}, 200)
        except stripe.error.CardError as e:
            return Response({"error": e.user_message}, 400)
        except Exception as e:  # noqa: BLE001
            return Response({"error": str(e)}, 400)


@csrf_exempt
def webhook(request):
    event = None
    payload = request.body
    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)

    payment_intent_id = event.data.object.id
    txn = StripeTranscation.objects.get(identifier=payment_intent_id)

    if event.type == "payment_intent.payment_failed":
        txn.status = TranscationStatus.FAILED
    if event.type == "payment_intent.succeeded":
        txn.status = TranscationStatus.SUCCESS
    if event.type == "payment_intent.processing":
        txn.status = TranscationStatus.PROCESSING
    if event.type == "payment_intent.created":
        print("webhook test done", payment_intent_id)  # noqa: T201
    txn.save(update_fields=["status"])
    return HttpResponse("", 200)
