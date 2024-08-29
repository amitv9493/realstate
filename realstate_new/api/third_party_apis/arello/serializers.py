from rest_framework import serializers
from utils import MissingFieldError


class ArelloSerializer(serializers.Serializer):
    license_jurisdiction = serializers.CharField(required=False)
    license_number = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get("license_number") and not attrs.get("first_name", None):
            msg = "Atleast first_name or license_number is required."
            raise MissingFieldError(msg)
        return super().validate(attrs)
