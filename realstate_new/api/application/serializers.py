from django.db import IntegrityError
from rest_framework import serializers

from realstate_new.application.models import JobApplication
from realstate_new.master.models.types import JOB_TYPE_MAPPINGS
from realstate_new.utils.serializers import DynamicModelSerializer
from realstate_new.utils.serializers import DynamicSerializer


class JobApplicationSerializer(DynamicSerializer):
    job_type = serializers.ChoiceField(
        choices=list(JOB_TYPE_MAPPINGS.keys()),
        write_only=True,
    )
    task_id = serializers.IntegerField()
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        user = self.context["request"].user
        data = validated_data
        job_instance = self.get_instance(data["job_type"], data["task_id"])
        try:
            instance = JobApplication.objects.create(
                content_object=job_instance,
                applicant=user,
            )
        except IntegrityError:
            msg = "Application Already Exists."
            raise serializers.ValidationError(msg, code="duplicate") from None

        if job_instance.application_type == "CLAIM":
            if job_instance.assigned_to is None:
                instance.status = "CLAIMED"
                job_instance.assigned_to = user
                instance.save(update_fields=["status"])
                job_instance.save(update_fields=["assigned_to"])
            else:
                msg = "already claimed."
                raise serializers.ValidationError(msg)

        return instance

    def validate(self, attrs):
        instance = self.get_instance(attrs["job_type"], attrs["task_id"])
        if instance and instance.assigned_to:
            msg = "This job as been assigned to someone already."
            raise serializers.ValidationError(msg, code="AlreadyAssigned")
        return super().validate(attrs)

    def get_instance(self, job_type, task_id):
        try:
            return JOB_TYPE_MAPPINGS[job_type].objects.get(id=task_id)
        except JOB_TYPE_MAPPINGS[job_type].DoesNotExist:
            return None

    def to_representation(self, instance):
        res = super().to_representation(instance)
        for k, v in JOB_TYPE_MAPPINGS.items():
            if instance.content_object.__class__ == v:
                res["job_type"] = k
                break
        return res


class Job(DynamicModelSerializer):
    class Meta:
        model = JobApplication
        fields = "__all__"
