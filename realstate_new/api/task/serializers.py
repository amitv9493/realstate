from rest_framework import serializers

from realstate_new.task.models import ShowingTask


class ShowingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowingTask
        fields = "__all__"
        extra_kwargs = {
            "created_by": {"read_only": True},
            "assigned_to": {"read_only": True},
        }


class Hello(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    username = serializers.CharField()
