import logging
from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.exceptions import PaymentVerificationFailedError

from realstate_new.payment.models import TranscationTypeChoice

from .serializers import ConfirmPaymentSerializer
from .serializers import PaymentSerializer

_logger = logging.getLogger(__name__)


class CreatePaymentView(APIView):
    serializer_class = PaymentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            payment_id = serializer.save()
            request.user.wallet.transaction.create(
                payment_id=payment_id,
                transcation_type=TranscationTypeChoice.WITHDRAW,
                amount=serializer.validated_data["amount"],
            )
            return Response({"payment_id": payment_id}, 200)


class ExecutePaymentView(APIView):
    serializer_class = ConfirmPaymentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            if serializer.save():
                data = serializer.validated_data
                user = self.request.user
                try:
                    with transaction.atomic():
                        tsc = user.wallet.transaction.all().get(
                            payment_id=data["payment_id"],
                        )
                        tsc.success = True
                        tsc.amount = data["amount"]
                        tsc.save(update_fields=["amount", "success"])
                        user.wallet.add_amount(
                            Decimal(data["amount"]),
                        )
                        user.save()
                except Exception:
                    _logger.exception("some error in the transcation block")
                    msg = "Internal server error contact admin"
                    raise APIException(msg) from None
                return Response(
                    {
                        "status": True,
                        "balance": user.wallet.balance,
                    },
                    200,
                )
            raise PaymentVerificationFailedError
