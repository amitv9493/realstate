from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from realstate_new.api.property.serializers import PropertySerializer
from realstate_new.api.user.serializers import UserSerializer
from realstate_new.master.models.property import Property
from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ProfessionalServiceTask
from realstate_new.task.models import RunnerTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models import SignTask
from realstate_new.utils.serializers import TrackingModelSerializer

EXTRA_FIELD = ["type_of_task"]
JOB_DASHBOARD_COMMON_FIELDS = [
    "id",
    "application_type",
    "task_time",
    "payment_amount",
    "created_by",
    "assigned_to",
    "property",
    "status",
    "notes",
    *EXTRA_FIELD,
]

PROPERTY_FIELDS = [
    "state",
    "zip",
    "street",
    "city",
    "latitude",
    "longitude",
    "asap",
    "vacant",
    "pets",
    "concierge",
    "alarm_code",
    "gate_code",
    "lockbox_type",
]

ONGOING_FIELDS = {
    "SHOWING": [*JOB_DASHBOARD_COMMON_FIELDS],
    "SIGN": [*JOB_DASHBOARD_COMMON_FIELDS, "task_type"],
    "RUNNER": [*JOB_DASHBOARD_COMMON_FIELDS, "task_type"],
    "PROFESSIONAL": [*JOB_DASHBOARD_COMMON_FIELDS, "service_type"],
    "OPENHOUSE": [*JOB_DASHBOARD_COMMON_FIELDS],
    "LOCKBOXBS": [*JOB_DASHBOARD_COMMON_FIELDS, "pickup_address", "task_type"],
    "LOCKBOXIR": [
        *JOB_DASHBOARD_COMMON_FIELDS,
        "pickup_address",
        "installation_or_remove_address",
        "task_type",
    ],
}
LATEST_TASK_FIELDS = [*JOB_DASHBOARD_COMMON_FIELDS, "application_status"]


class TaskSerializer(TrackingModelSerializer):
    assigned_to = UserSerializer(
        fields=["username", "first_name", "last_name", "email", "phone"],
        read_only=True,
    )
    application_status = serializers.SerializerMethodField()

    type_of_task = serializers.CharField(read_only=True)

    class Meta:
        extra_kwargs = {
            "created_by": {"read_only": True},
        }

    def get_application_status(self, obj):
        request = self.context.get("request")
        application = obj.applications.filter(applicant=request.user).first()
        if application:
            return application.status
        return None

    @staticmethod
    def get_property_fields():
        return PROPERTY_FIELDS


class ShowingTaskSerializer(TaskSerializer):
    property_address = PropertySerializer(
        fields=PROPERTY_FIELDS,
        required=True,
        many=True,
    )

    class Meta(TaskSerializer.Meta):
        model = ShowingTask
        fields = "__all__"

    def create(self, validated_data: Any) -> Any:
        property_addresses = validated_data.pop("property_address", None)
        instance = super().create(validated_data)
        for address in property_addresses:
            Property.objects.create(**address, task=instance)
        return instance

    def to_representation(self, instance: Any) -> dict[str, Any]:
        data = super().to_representation(instance)
        data["property_address"] = PropertySerializer(
            instance.property_address.all(),
            many=True,
        ).data
        return data


class LockBoxBSSerializer(TaskSerializer):
    pickup_address = PropertySerializer(fields=PROPERTY_FIELDS)

    class Meta(TaskSerializer.Meta):
        model = LockBoxTaskBS
        fields = "__all__"
        exclude_fields = [
            "installation_or_remove_address",
            "property",
        ]

    def create(self, validated_data: Any) -> Any:
        pickup_address = validated_data.pop("pickup_address", None)
        instance = super().create(validated_data)
        if pickup_address:
            pickup_address_rec = Property.objects.create(
                **pickup_address,
                task=instance,
            )
            instance.pickup_address = pickup_address_rec
            instance.save(update_fields=["pickup_address"])
        return instance


class LockBoxIRSerializer(TaskSerializer):
    pickup_address = PropertySerializer(required=True, fields=PROPERTY_FIELDS)
    installation_or_remove_address = PropertySerializer(
        required=True,
        fields=PROPERTY_FIELDS,
    )

    class Meta(TaskSerializer.Meta):
        model = LockBoxTaskIR
        fields = "__all__"
        exclude_fields = ("property",)

    def create(self, validated_data: Any) -> Any:
        installation_or_remove_address = validated_data.pop(
            "installation_or_remove_address",
            None,
        )
        pickup_address = validated_data.pop("pickup_address", None)

        instance = super().create(validated_data)
        ir_addr = Property.objects.create(
            **installation_or_remove_address,
            task=instance,
        )
        pickup_addr = Property.objects.create(**pickup_address, task=instance)
        instance.pickup_address = pickup_addr
        instance.installation_or_remove_address = ir_addr
        instance.save(
            update_fields=["installation_or_remove_address", "pickup_address"],
        )

        return instance


class OpenHouseTaskSerializer(TaskSerializer):
    property_address = PropertySerializer(fields=PROPERTY_FIELDS, required=True)

    class Meta(TaskSerializer.Meta):
        model = OpenHouseTask
        fields = "__all__"

    def create(self, validated_data: Any) -> Any:
        property_address = validated_data.pop("property_address")
        instance = super().create(validated_data)
        property_rec = Property.objects.create(**property_address, task=instance)
        instance.property_address = property_rec
        instance.save(update_fields=["property_address"])
        return instance


class ProfessionalTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = ProfessionalServiceTask
        fields = "__all__"


class RunnerTaskSerializer(TaskSerializer):
    property_address = PropertySerializer(fields=PROPERTY_FIELDS, required=True)

    class Meta(TaskSerializer.Meta):
        model = RunnerTask
        fields = "__all__"

    def create(self, validated_data: Any) -> Any:
        property_address = validated_data.pop("property_address")
        instance = super().create(validated_data)
        property_rec = Property.objects.create(**property_address, task=instance)
        instance.property_address = property_rec
        instance.save(update_fields=["property_address"])
        return instance


class SignTaskSerializer(TaskSerializer):
    install_address = PropertySerializer(
        required=False,
        fields=PROPERTY_FIELDS,
    )
    pickup_address = PropertySerializer(
        required=False,
        fields=PROPERTY_FIELDS,
    )
    remove_address = PropertySerializer(
        required=False,
        fields=PROPERTY_FIELDS,
    )
    dropoff_address = PropertySerializer(
        required=False,
        fields=PROPERTY_FIELDS,
    )

    class Meta(TaskSerializer.Meta):
        model = SignTask
        fields = "__all__"
        exclude_fields = ["property"]

    def create(self, validated_data: Any) -> Any:
        install_address = validated_data.pop("install_address", None)
        pickup_address = validated_data.pop("pickup_address", None)
        remove_address = validated_data.pop("remove_address", None)
        dropoff_address = validated_data.pop("dropoff_address", None)

        instance = super().create(validated_data)
        if validated_data["task_type"] == "INSTALL":
            install_address_rec = Property.objects.create(
                **install_address,
                task=instance,
            )
            pickup_address_rec = Property.objects.create(
                **pickup_address,
                task=instance,
            )
            instance.pickup_address = pickup_address_rec
            instance.install_address = install_address_rec

        elif validated_data["task_type"] == "REMOVE":
            remove_address_rec = Property.objects.create(
                **remove_address,
                task=instance,
            )
            dropoff_address_rec = Property.objects.create(
                **dropoff_address,
                task=instance,
            )
            instance.dropoff_address = dropoff_address_rec
            instance.remove_address = remove_address_rec
        return instance

    def to_representation(self, instance: Any) -> dict[str, Any]:
        rep = super(TrackingModelSerializer, self).to_representation(instance)
        if instance.task_type == "INSTALL":
            rep.pop("remove_address", None)
            rep.pop("dropoff_address", None)

        if instance.task_type == "REMOVE":
            rep.pop("install_address", None)
            rep.pop("pickup_address", None)
        return rep


class OngoingTaskSerializer(serializers.Serializer):
    Showing = ShowingTaskSerializer(
        many=True,
        fields=ONGOING_FIELDS["SHOWING"],
        required=False,
    )
    Sign = SignTaskSerializer(
        many=True,
        fields=ONGOING_FIELDS["SIGN"],
        required=False,
    )
    Runner = RunnerTaskSerializer(
        many=True,
        fields=ONGOING_FIELDS["RUNNER"],
        required=False,
    )
    Professional = ProfessionalTaskSerializer(
        many=True,
        fields=ONGOING_FIELDS["PROFESSIONAL"],
        required=False,
    )
    OpenHouse = OpenHouseTaskSerializer(
        many=True,
        fields=ONGOING_FIELDS["OPENHOUSE"],
        required=False,
    )
    LockBoxIR = LockBoxBSSerializer(
        many=True,
        fields=ONGOING_FIELDS["LOCKBOXBS"],
        required=False,
    )
    LockBoxBS = LockBoxIRSerializer(
        many=True,
        fields=ONGOING_FIELDS["LOCKBOXIR"],
        required=False,
    )


class LatestTaskSerializer(serializers.Serializer):
    showing_tasks = ShowingTaskSerializer(
        many=True,
        fields=[*LATEST_TASK_FIELDS],
    )
    sign_tasks = SignTaskSerializer(
        many=True,
        fields=[*LATEST_TASK_FIELDS, "task_type"],
    )
    runner_tasks = RunnerTaskSerializer(
        many=True,
        fields=[*LATEST_TASK_FIELDS, "task_type"],
    )
    professional_tasks = ProfessionalTaskSerializer(
        many=True,
        fields=[*LATEST_TASK_FIELDS, "service_type"],
    )
    openhouse_tasks = OpenHouseTaskSerializer(many=True, fields=LATEST_TASK_FIELDS)
    lockbox_tasks_bs = LockBoxBSSerializer(
        many=True,
        fields=[*LATEST_TASK_FIELDS, "pickup_address", "task_type"],
    )
    lockbox_tasks_ir = LockBoxIRSerializer(
        many=True,
        fields=[
            *LATEST_TASK_FIELDS,
            "pickup_address",
            "installation_or_remove_address",
            "task_type",
        ],
    )


class TaskActionSerializer(serializers.Serializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False,
    )
