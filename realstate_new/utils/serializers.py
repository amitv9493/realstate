from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer


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
        # use only to remove some fields from model Serializer
        exclude_fields = getattr(self.Meta, "exclude_fields", None)
        if exclude_fields:
            for field in exclude_fields:
                self.fields.pop(field)


class DynamicSerializer(DynamicFieldsMixin, Serializer): ...
