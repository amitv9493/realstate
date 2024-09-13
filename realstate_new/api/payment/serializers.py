import paypalrestsdk
import paypalrestsdk.exceptions
from rest_framework import serializers

from realstate_new.utils.serializers import DynamicSerializer


class PaymentSerializer(DynamicSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        amount = validated_data["amount"]
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
            return payment.id

        raise serializers.ValidationError(payment.errors)


class ConfirmPaymentSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    payer_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        data = validated_data
        try:
            payment = paypalrestsdk.Payment.find(data["payment_id"])
        except paypalrestsdk.exceptions.ResourceNotFound:
            msg = "given payment id is incorrect"
            raise serializers.ValidationError(msg) from None

        if payment.execute({"payer_id": data["payer_id"]}):
            return True
        return None
