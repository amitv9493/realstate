from typing import Any

from rest_framework import serializers

from realstate_new.api.property.serializers import PropertySerializer
from realstate_new.master.models.property import Property
from realstate_new.task.models import LockBox
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
    "job_type",
    "task_time",
    "payment_amount",
    "created_by",
    "assigned_to",
    "property",
    *EXTRA_FIELD,
]

PROPERTY_FIELDS = [
    "state",
    "zip",
    "street",
    "city",
    "latitude",
    "longitude",
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
    application_status = serializers.SerializerMethodField()

    type_of_task = serializers.CharField(read_only=True)
    property = PropertySerializer(
        fields=PROPERTY_FIELDS,
        required=False,
    )

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

    def create(self, validated_data: Any) -> Any:
        property_address = validated_data.pop("property", None)
        if property_address:
            property_instance = Property.objects.create(
                **property_address,
            )
            validated_data["property"] = property_instance
        return super().create(validated_data)

    @staticmethod
    def get_property_fields():
        return PROPERTY_FIELDS


class ShowingTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = ShowingTask
        fields = "__all__"


class LockBoxSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = LockBox
        fields = "__all__"
        exclude_fields = ["id", "lockbox_task"]


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
        if pickup_address:
            pickup_address_rec = Property.objects.create(**pickup_address)
            validated_data["pickup_address"] = pickup_address_rec

        return super().create(validated_data)


class LockBoxIRSerializer(TaskSerializer):
    pickup_address = PropertySerializer(required=False, fields=PROPERTY_FIELDS)
    installation_or_remove_address = PropertySerializer(
        required=False,
        fields=PROPERTY_FIELDS,
    )

    class Meta(TaskSerializer.Meta):
        model = LockBoxTaskIR
        fields = "__all__"
        exclude_fields = ("property",)

    def create(self, validated_data: Any) -> Any:
        installation_or_remove_address = validated_data.get(
            "installation_or_remove_address",
        )
        pickup_address = validated_data.get("pickup_address")
        if installation_or_remove_address:
            validated_data["installation_or_remove_address"] = Property.objects.create(
                **installation_or_remove_address,
            )
        if pickup_address:
            validated_data["pickup_address"] = Property.objects.create(**pickup_address)

        return super().create(validated_data)


class OpenHouseTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = OpenHouseTask
        fields = "__all__"


class ProfessionalTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = ProfessionalServiceTask
        fields = "__all__"


class RunnerTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        model = RunnerTask
        fields = "__all__"


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

        if validated_data["task_type"] == "INSTALL":
            validated_data["install_address"] = Property.objects.create(
                **install_address,
            )
            validated_data["pickup_address"] = Property.objects.create(**pickup_address)

        elif validated_data["task_type"] == "REMOVE":
            validated_data["remove_address"] = Property.objects.create(**remove_address)
            validated_data["dropoff_address"] = Property.objects.create(
                **dropoff_address,
            )

        return super().create(validated_data)

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
    )
    Sign = SignTaskSerializer(many=True, fields=ONGOING_FIELDS["SIGN"])
    Runner = RunnerTaskSerializer(many=True, fields=ONGOING_FIELDS["RUNNER"])
    Professional = ProfessionalTaskSerializer(
        many=True,
        fields=ONGOING_FIELDS["PROFESSIONAL"],
    )
    OpenHouse = OpenHouseTaskSerializer(
        many=True,
        fields=ONGOING_FIELDS["OPENHOUSE"],
    )
    LockBoxIR = LockBoxBSSerializer(
        many=True,
        fields=ONGOING_FIELDS["LOCKBOXBS"],
    )
    LockBoxBS = LockBoxIRSerializer(
        many=True,
        fields=ONGOING_FIELDS["LOCKBOXIR"],
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
