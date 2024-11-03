import logging

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from realstate_new.payment.models import Transcation
from realstate_new.payment.models.choices import PaymentStatusChoices
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
