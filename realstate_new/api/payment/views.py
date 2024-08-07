import logging
from decimal import Decimal

import paypalrestsdk
import paypalrestsdk.exceptions
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

_logger = logging.getLogger(__name__)


class CreatePaymentView(APIView):
    class PaymentSerializer(serializers.Serializer):
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    serializer_class = PaymentSerializer

    def post(self, request):
        amount = request.data.get("amount")
        if not amount:
            msg = "Amount is required to create payment."
            raise serializers.ValidationError(msg)

        payment = paypalrestsdk.Payment(
            {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": "http://localhost:3000/payment/success",
                    "cancel_url": "http://localhost:3000/payment/cancel",
                },
                "transactions": [
                    {
                        "amount": {"total": str(amount), "currency": "USD"},
                        "description": "Payment for Item",
                    },
                ],
            },
        )

        if payment.create():
            return Response({"paymentId": payment.id})
        return Response({"error": payment.error})


class ExecutePaymentView(APIView):
    class ConfirmPaymentSerializer(serializers.Serializer):
        payment_id = serializers.CharField()
        payer_id = serializers.CharField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    serializer_class = ConfirmPaymentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            try:
                payment = paypalrestsdk.Payment.find(data["payment_id"])
            except paypalrestsdk.exceptions.ResourceNotFound:
                msg = "given payment id is incorrect"
                raise serializers.ValidationError(msg) from None

            if payment.execute({"payer_id": data["payer_id"]}):
                user = request.user
                user.wallet.add_amount(Decimal(data["amount"]))
                user.save(update_fields=["balance"])

                return Response(
                    {
                        "success": True,
                        "message": "Payment successful and wallet updated",
                        "new_balance": str(user.wallet.balance),
                    },
                )

        return Response({"error": payment.error})
