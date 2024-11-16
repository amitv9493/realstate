import json
import logging
from typing import TYPE_CHECKING

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
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

if TYPE_CHECKING:
    from realstate_new.task.models.basetask import BaseTask

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
        task_id = serializers.IntegerField()
        task_type = serializers.ChoiceField(choices=list(JOB_TYPE_MAPPINGS.keys()))
        payment_method_id = serializers.CharField(max_length=255, required=False)
        should_save_payment_method = serializers.BooleanField(
            required=False,
            default=True,
        )

    serializer_class = PaymentSerialier

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            data = serializer.validated_data
            try:
                task: BaseTask = get_job(
                    job_model=data["task_type"],
                    task_id=data["task_id"],
                )

                intent_id, client_secret = self.create_intent_simple(
                    amt=task.payment_amt_for_task_creater,
                )
            except ObjectDoesNotExist as e:
                msg = {"task": "task does not exists"}
                raise ValidationError(msg) from e

            except Exception as e:  # noqa: BLE001
                return Response({"error": str(e)}, 400)
            else:
                StripeTranscation.objects.create(
                    content_type=ContentType.objects.get_for_model(
                        task,
                        for_concrete_model=False,
                    ),
                    object_id=task.id,
                    user=request.user,
                    amt=task.payment_amt_for_task_creater,
                    status=TranscationStatus.INITIATED,
                    txn_type=TxnType.PAYIN,
                    identifier=intent_id,
                )
                data = {
                    "amt": task.payment_amount,
                    "client_secret": client_secret,
                    "platform_fees": task.platform_fees,
                    "stripe_fees": round(task.stripe_fees, 2),
                    "total_amt": task.payment_amt_for_task_creater,
                }
                return Response(data, 200)

    def create_intent_simple(self, amt):
        params = {
            "amount": int(amt * 100),
            "currency": "usd",
            "automatic_payment_methods": {
                "enabled": True,
            },
        }
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
def test_webhook(request):
    event = None
    payload = request.body
    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)

    payment_intent = event.data.object
    if event.type == "payment_intent.succeeded":
        _logger.info(event.type)
        _logger.info(payment_intent)

    return HttpResponse("", 200)


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
    msg = f"processing the payment intent with this identifier: {payment_intent_id}"
    _logger.info(msg)
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


class StripeConnectAccount:
    def post(self, request, *args, **kwargs):
        try:
            account = stripe.Account.create(
                controller={
                    "stripe_dashboard": {
                        "type": "express",
                    },
                    "fees": {"payer": "application"},
                    "losses": {"payments": "application"},
                },
            )

            return Response({"account": account.id})
        except Exception as e:  # noqa: BLE001
            return Response({"error": str(e)}, 500)


class ConnectAccountCreateView(APIView):
    def refresh_link(self, acc_id):
        return self.request.build_absolute_uri(
            reverse("api:refresh-link", kwargs={"account_id": acc_id}),
        )

    def return_link(self, acc_id):
        return self.request.build_absolute_uri(
            reverse("api:return-link", kwargs={"account_id": acc_id}),
        )

    def post(self, request, *args, **kwargs):
        if acc_id := request.user.stripe_account_id:
            account_link = stripe.AccountLink.create(
                account=acc_id,
                refresh_url=self.refresh_link(acc_id),
                return_url=self.return_link(acc_id),
                type="account_onboarding",
            )
            return Response(
                {
                    "account_link": account_link.url,
                    "account": acc_id,
                },
            )

        try:
            # Create Standard Connect account
            account = stripe.Account.create(
                type="express",
                email=request.user.email,
                country="US",
                business_type="individual",
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
            )

            # Generate account link for onboarding

            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url=self.refresh_link(account.id),
                return_url=self.return_link(account.id),
                type="account_onboarding",
            )
        except Exception as e:  # noqa: BLE001
            return Response({"error": str(e)}, 500)
        else:
            request.user.stripe_account_id = account.id
            request.user.save(update_fields=["stripe_account_id"])
            return Response(
                {
                    "account": account.id,
                    "account_link": account_link.url,
                },
            )


class AccountStatusView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        if user.stripe_account_id:
            data = {
                "is_details_submitted": user.is_details_submitted,
                "is_charges_enabled": user.is_charges_enabled,
                "is_payouts_enabled": user.is_payouts_enabled,
                "stripe_account_id": user.stripe_account_id,
            }
            return Response(data, status.HTTP_200_OK)
        return Response(
            {"error": "Stripe accoount hasnt been created yet."},
            status.HTTP_400_BAD_REQUEST,
        )


def get_refresh_link(request, account_id):
    try:
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=request.build_absolute_uri(
                reverse("api:refresh-link", kwargs={"account_id": account_id}),
            ),
            return_url="https://www.google.com",
            type="account_onboarding",
        )
        return HttpResponseRedirect(account_link.url)

    except Exception as e:  # noqa: BLE001
        return HttpResponse(str(e), 400)


def get_return_link(request, account_id):
    return HttpResponse("thanks for onboarding with us.", 200)


@csrf_exempt
def account_update_webhook(request):
    event = None
    payload = request.body
    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError:
        return HttpResponse(status=400)

    if event.type == "account.updated":
        acc_id = event.account
        try:
            user = get_user_model().objects.get(stripe_account_id=acc_id)
        except get_user_model().DoesNotExist:
            return HttpResponse("", 200)
        user.is_details_submitted = event.data.object["details_submitted"]
        user.is_charges_enabled = event.data.object["charges_enabled"]
        user.is_payouts_enabled = event.data.object["payouts_enabled"]
        user.save(
            update_fields=[
                "is_details_submitted",
                "is_charges_enabled",
                "is_payouts_enabled",
            ],
        )
        msg = f"Successfully processed the event for account_id: \
                {acc_id} username:{request.user.username}"
        _logger.info(msg)
    return HttpResponse("", 200)
