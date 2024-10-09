import logging

from django.conf import settings
from django.db import transaction
from paypalhttp import HttpError
from paypalpayoutssdk.payouts import PayoutsGetRequest
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from realstate_new.payment.models import TranscationTypeChoice
from realstate_new.utils.exceptions import PaymentVerificationFailedError

from .serializers import ConfirmPaymentSerializer
from .serializers import PaymentSerializer

_logger = logging.getLogger(__name__)


class CreatePaymentView(APIView):
    serializer_class = PaymentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            payment_id = serializer.save()
            request.user.transactions.create(
                payment_id=payment_id,
                transcation_type=TranscationTypeChoice.DIPOSIT,
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
                user = request.user
                try:
                    with transaction.atomic():
                        tsc = user.transactions.get(
                            payment_id=data["payment_id"],
                        )
                        tsc.success = True
                        tsc.amount = data["amount"]
                        tsc.save(update_fields=["amount", "success"])
                        user.save()
                except Exception:
                    _logger.exception("some error in the transcation block")
                    msg = "Internal server error contact admin"
                    raise APIException(msg) from None
                return Response(
                    {
                        "status": True,
                    },
                    200,
                )
            raise PaymentVerificationFailedError


class CreatepaypalBatchView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        request = PayoutsGetRequest("batch_id")

        try:
            response = settings.CLIENT.execute(request)
            batch_status = response.result.batch_header.batch_status
            _logger.info(batch_status)
        except OSError as ioe:
            if isinstance(ioe, HttpError):
                pass
        return Response("", 200)
