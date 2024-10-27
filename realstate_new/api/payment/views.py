import logging

import braintree
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from realstate_new.payment.models import Transcation
from realstate_new.payment.models.choices import PayymentStatusChoices

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
    def post(self, request, *args, **kwargs):
        nonce = request.data.get("nonce", None)
        amt = request.data.get("amt", None)

        if not nonce or not amt:
            return Response(data={"error": "amt or nonce missing"}, status=400)

        try:
            result = gateway.transaction.sale(
                {
                    "amount": amt,
                    "payment_method_nonce": nonce,
                    "options": {"submit_for_settlement": True},
                },
            )

            if result.is_success:
                Transcation.objects.create(
                    user=request.user,
                    transcation_id=result.transaction.id,
                    status=PayymentStatusChoices.SUCCESS,
                )
                return Response(
                    {
                        "success": True,
                        "transaction_id": result.transaction.id,
                        "message": "Payment processed successfully",
                    },
                )
            if result.transaction:
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

        except braintree.exceptions.BraintreeError as e:
            return Response({"success": False, "error": str(e)}, status=500)
