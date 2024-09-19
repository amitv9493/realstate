from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from realstate_new.utils import MissingFieldError

User = get_user_model()


class ArelloSerializer(serializers.Serializer):
    license_jurisdiction = serializers.CharField(required=True)
    license_number = serializers.CharField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this license number already exists!",
            ),
        ],
    )
    last_name = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get("license_number") and not attrs.get("first_name", None):
            msg = "Atleast first_name or license_number is required."
            raise MissingFieldError(msg)
        return super().validate(attrs)
