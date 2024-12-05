from rest_framework import serializers

from realstate_new.payment.models.stripe import StripeTranscation
from realstate_new.task.models import JOB_TYPE_MAPPINGS


class PaymentVerificationSerializer(serializers.Serializer):
    nonce = serializers.CharField()
    amt = serializers.CharField()
    task_type = serializers.ChoiceField(choices=list(JOB_TYPE_MAPPINGS.keys()))
    task_id = serializers.CharField()


class TransactionIDSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["identifier"]
        model = StripeTranscation
