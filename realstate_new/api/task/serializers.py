from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from realstate_new.api.property.serializers import LockBoxSerializer
from realstate_new.api.property.serializers import PropertySerializer
from realstate_new.api.user.serializers import UserSerializer
from realstate_new.payment.models.stripe import StripeTranscation
from realstate_new.task.models import LockBoxTaskBS
from realstate_new.task.models import LockBoxTaskIR
from realstate_new.task.models import OpenHouseTask
from realstate_new.task.models import ProfessionalServiceTask
from realstate_new.task.models import RunnerTask
from realstate_new.task.models import ShowingTask
from realstate_new.task.models import SignTask
from realstate_new.task.models import VerificationDocument
from realstate_new.task.models.choices import TaskStatusChoices
from realstate_new.task.models.open_for_vendor_task import OpenForVendorTask
from realstate_new.task.models.open_for_vendor_task import VendorType
from realstate_new.utils.serializers import DynamicModelSerializer
from realstate_new.utils.serializers import TrackingModelSerializer

EXTRA_FIELD = ["type_of_task", "payment_verified", "txn_ids"]
JOB_DASHBOARD_COMMON_FIELDS = [
    "id",
    "application_type",
    "task_time",
    "payment_amount",
    "created_by",
    "assigned_to",
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
    "lockbox",
]

ONGOING_FIELDS = {
    "SHOWING": [*JOB_DASHBOARD_COMMON_FIELDS, "property_address"],
    "SIGN": [*JOB_DASHBOARD_COMMON_FIELDS, "task_type"],
    "RUNNER": [*JOB_DASHBOARD_COMMON_FIELDS, "task_type", "property_address"],
    "PROFESSIONAL": [*JOB_DASHBOARD_COMMON_FIELDS, "service_type"],
    "OPENHOUSE": [*JOB_DASHBOARD_COMMON_FIELDS, "property_address"],
    "LOCKBOXBS": [
        *JOB_DASHBOARD_COMMON_FIELDS,
        "pickup_address",
        "task_type",
        "lockbox",
    ],
    "LOCKBOXIR": [
        *JOB_DASHBOARD_COMMON_FIELDS,
        "pickup_address",
        "installation_or_remove_address",
        "task_type",
        "lockbox",
    ],
    "OPENFORVENDOR": [*JOB_DASHBOARD_COMMON_FIELDS, "property-address"],
}
LATEST_TASK_FIELDS = [*JOB_DASHBOARD_COMMON_FIELDS, "application_status"]


class TaskSerializer(TrackingModelSerializer):
    assigned_to = UserSerializer(
        fields=["username", "first_name", "last_name", "email", "phone"],
        read_only=True,
    )
    application_status = serializers.SerializerMethodField()

    type_of_task = serializers.CharField(read_only=True)
    txn_ids = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            "created_by": {"read_only": True},
        }

    def get_txn_ids(self, obj):
        return list(
            StripeTranscation.objects.filter(
                content_type=ContentType.objects.get_for_model(obj.__class__),
                object_id=obj.id,
                user=obj.created_by,
                txn_type="PAYIN",
            ).values_list("identifier", flat=True),
        )
        return []

    def get_application_status(self, obj):
        request = self.context.get("request")
        application = obj.applications.filter(applicant=request.user).first()
        if application:
            return application.status
        return None

    @staticmethod
    def get_property_fields():
        return PROPERTY_FIELDS

    @property
    def request(self):
        return self.context.get("request", None)

    def save_property_instance(
        self,
        task,
        request,
        *,
        property_validated_data: dict,
        many=False,
    ):
        if many:
            return [
                PropertySerializer(context={"request": request}).create(
                    validated_data=address | {"task": task},
                )
                for address in property_validated_data
            ]
        return PropertySerializer(context={"request": request}).create(
            validated_data=property_validated_data | {"task": task},
        )


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
        property_addresses = validated_data.pop("property_address", [])
        instance = super().create(validated_data)

        properties = self.save_property_instance(
            task=instance,
            request=self.request,
            property_validated_data=property_addresses,
            many=True,
        )

        instance.property_address.set(properties)
        return instance


class LockBoxBSSerializer(TaskSerializer):
    pickup_address = PropertySerializer(fields=PROPERTY_FIELDS)
    lockbox = LockBoxSerializer(required=False)

    class Meta(TaskSerializer.Meta):
        model = LockBoxTaskBS
        fields = "__all__"
        exclude_fields = [
            "installation_or_remove_address",
            "property",
        ]

    def create(self, validated_data: Any) -> Any:
        pickup_address = validated_data.pop("pickup_address", None)
        lockbox = validated_data.pop("lockbox", None)
        instance = super().create(validated_data)
        lockbox_instance = LockBoxSerializer().create(validated_data=lockbox) if lockbox else None
        update_fields = []
        instance.lockbox = lockbox_instance
        update_fields.append("lockbox")
        if pickup_address:
            p_instance = self.save_property_instance(
                task=instance,
                request=self.request,
                property_validated_data=pickup_address,
            )

            instance.pickup_address = p_instance
            update_fields.append("pickup_address")
        instance.save(update_fields=update_fields)
        return instance


class LockBoxIRSerializer(TaskSerializer):
    pickup_address = PropertySerializer(required=True, fields=PROPERTY_FIELDS)
    lockbox = LockBoxSerializer(required=False)

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
        lockbox = validated_data.pop("lockbox", None)
        instance = super().create(validated_data)
        lockbox_instance = LockBoxSerializer().create(validated_data=lockbox) if lockbox else None
        instance.lockbox = lockbox_instance
        ir_addr = self.save_property_instance(
            task=instance,
            request=self.request,
            property_validated_data=installation_or_remove_address,
        )
        pickup_addr = self.save_property_instance(
            task=instance,
            request=self.request,
            property_validated_data=pickup_address,
        )
        instance.pickup_address = pickup_addr
        instance.installation_or_remove_address = ir_addr
        instance.save(
            update_fields=[
                "installation_or_remove_address",
                "pickup_address",
                "lockbox",
            ],
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

        property_rec = self.save_property_instance(
            task=instance,
            request=self.request,
            property_validated_data=property_address,
        )
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
        property_rec = self.save_property_instance(
            task=instance,
            request=self.request,
            property_validated_data=property_address,
        )
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
            install_address_rec = self.save_property_instance(
                task=instance,
                request=self.request,
                property_validated_data=install_address,
            )
            pickup_address_rec = self.save_property_instance(
                task=instance,
                request=self.request,
                property_validated_data=pickup_address,
            )
            instance.pickup_address = pickup_address_rec
            instance.install_address = install_address_rec

        elif validated_data["task_type"] == "REMOVE":
            remove_address_rec = self.save_property_instance(
                task=instance,
                request=self.request,
                property_validated_data=remove_address,
            )
            dropoff_address_rec = self.save_property_instance(
                task=instance,
                request=self.request,
                property_validated_data=dropoff_address,
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


class VendorTypeSerializer(DynamicModelSerializer):
    class Meta:
        model = VendorType
        fields = "__all__"


class OpenForVendorTaskSerializer(TaskSerializer):
    property_address = PropertySerializer(
        fields=PROPERTY_FIELDS,
        required=True,
        many=True,
    )

    def to_representation(self, instance: Any) -> dict[str, Any]:
        data = super().to_representation(instance)
        data["open_for_vendor"] = str(instance.open_for_vendor)
        return data

    class Meta(TaskSerializer.Meta):
        model = OpenForVendorTask
        fields = "__all__"

    def create(self, validated_data: Any) -> Any:
        property_address = validated_data.pop("property_address")
        instance = super().create(validated_data)

        properties = self.save_property_instance(
            task=instance,
            request=self.request,
            property_validated_data=property_address,
            many=True,
        )
        instance.property_address.set(properties)
        return instance


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

    OpenForVendor = OpenForVendorTaskSerializer(
        many=True,
        fields=ONGOING_FIELDS["OPENFORVENDOR"],
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
    class ImageSeralizer(serializers.Serializer):
        image = serializers.ImageField()

    image_list = serializers.ListField(child=serializers.ImageField(), required=False)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False,
    )

    def validate(self, attrs: Any) -> Any:
        if self.context.get("task_action", "").upper() == TaskStatusChoices.MARK_COMPLETED:
            if not attrs.get("image_list", None):
                msg = "image_list is a required field when marking task completed"
                raise serializers.ValidationError({"image_list": msg}, code="required")
        return super().validate(attrs)


class VerificationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDocument
        fields = ["image", "created_at"]
