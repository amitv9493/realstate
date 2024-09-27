import logging
from typing import Any
from warnings import warn

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer

from realstate_new.utils import TrackingModel

_logger = logging.getLogger(__name__)


class FieldExceptionError(Exception):
    pass


class DynamicFieldsMixin:
    def __init__(self, *args, **kwargs):
        depth = kwargs.pop("depth", None)
        fields = kwargs.pop("fields", None)
        remove_fields = kwargs.pop("remove_fields", None)
        super().__init__(*args, **kwargs)
        context_fields = self.context.get("fields", None)
        if depth is not None:
            self.Meta.depth = depth

        if fields and remove_fields:
            msg = ("Cannot set both field and remove_field attribute on dynamic serializer",)

            raise FieldExceptionError(msg=msg)
        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if remove_fields:
            for field in remove_fields:
                self.fields.pop(field)

        if context_fields:
            allowed = set(context_fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class DynamicModelSerializer(DynamicFieldsMixin, ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if issubclass(self.Meta.model, TrackingModel):
            if not isinstance(self, TrackingModelSerializer):
                warn(
                    f"Serializer {self.__class__.__name__} is using a model "
                    f"that inherits from TrackingModel. Consider using "
                    f"TrackingSerializer instead of {self.__class__.__name__}.",
                    stacklevel=1,
                )
        # use only to remove some fields from model Serializer
        exclude_fields = getattr(self.Meta, "exclude_fields", None)
        if exclude_fields:
            for field in exclude_fields:
                if field in self.fields:
                    self.fields.pop(field)


class DynamicSerializer(DynamicFieldsMixin, Serializer):
    pass


class TrackingSerializer(DynamicSerializer):
    def set_created_by(self, validated_data):
        validated_data["created_by"] = self.context.get("request").user


class TrackingModelSerializer(DynamicModelSerializer):
    def create(self, validated_data: Any) -> Any:
        self.set_created_by(validated_data)
        return super().create(validated_data)

    def set_created_by(self, validated_data):
        validated_data["created_by"] = self.context.get("request").user
