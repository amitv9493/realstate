from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from realstate_new.api.application.serializers import JobApplicationModelSerializer
from realstate_new.api.payment.serializers import TransactionIDSerializer
from realstate_new.api.property.serializers import LockBoxSerializer
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
from realstate_new.task.models import VerificationDocument
from realstate_new.task.models.choices import SignTaskType
from realstate_new.task.models.choices import TaskStatusChoices
from realstate_new.task.models.open_for_vendor_task import OpenForVendorTask
from realstate_new.task.models.open_for_vendor_task import VendorType
from realstate_new.utils.exceptions import PropertyNotFound
from realstate_new.utils.serializers import DynamicModelSerializer
from realstate_new.utils.serializers import TrackingModelSerializer

JOB_CREATER_SPECIFIC_FIELDS = [
    "payment_verified",
    "txn_ids",
    "applications",
    "payment_amount",
]
TASK_COMMON_FIELDS = [
    "id",
    "application_type",
    "task_time",
    "created_by",
    "assigned_to",
    "status",
    "notes",
    "type_of_task",
    "receivable_amount",
]

PROPERTY_FIELDS = [
    "id",
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
    "lockbox",
    "delete",
]

DASHBOARD_COMMON_FIELDS = {
    "SHOWING": [*TASK_COMMON_FIELDS, "property_address"],
    "SIGN": [
        *TASK_COMMON_FIELDS,
        "task_type",
        "install_address",
        "pickup_address",
        "remove_address",
        "dropoff_address",
    ],
    "RUNNER": [*TASK_COMMON_FIELDS, "task_type", "property_address"],
    "PROFESSIONAL": [*TASK_COMMON_FIELDS, "service_type"],
    "OPENHOUSE": [*TASK_COMMON_FIELDS, "property_address"],
    "LOCKBOXBS": [
        *TASK_COMMON_FIELDS,
        "pickup_address",
        "task_type",
        "lockbox",
    ],
    "LOCKBOXIR": [
        *TASK_COMMON_FIELDS,
        "pickup_address",
        "installation_or_remove_address",
        "task_type",
        "lockbox",
    ],
    "OPENFORVENDOR": [*TASK_COMMON_FIELDS, "property_address"],
}
JOB_CREATER_FIELDS = {
    k: v + JOB_CREATER_SPECIFIC_FIELDS for k, v in DASHBOARD_COMMON_FIELDS.items()
}
JOB_SEEKER_FIELDS = DASHBOARD_COMMON_FIELDS


class TaskSerializer(TrackingModelSerializer):
    assigned_to = UserSerializer(
        fields=["username", "first_name", "last_name", "email", "phone"],
        read_only=True,
    )
    application_status = serializers.SerializerMethodField()

    type_of_task = serializers.CharField(read_only=True)
    txn = TransactionIDSerializer(many=True, read_only=True)
    applications = JobApplicationModelSerializer(read_only=True, many=True)
    receivable_amount = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        read_only=True,
        source="payment_amt_for_payout",
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

    def update(self, instance: Any, validated_data: Any) -> Any:
        property_addresses = validated_data.pop("property_address", [])
        property_objects = list(instance.property_address.all())
        if property_addresses:
            for address in property_addresses:
                is_delete = address.pop("delete", False)
                if property_id := address.get("id", None):
                    try:
                        property_instance = Property.objects.get(id=property_id)
                    except Property.DoesNotExist:
                        raise PropertyNotFound(property_id=property_id) from None

                    if not is_delete:
                        PropertySerializer().update(property_instance, address)

                    else:
                        property_instance.delete()
                else:
                    property_objects.append(
                        self.save_property_instance(
                            task=instance,
                            request=self.request,
                            property_validated_data=address,
                            many=False,
                        ),
                    )

            instance.property_address.set(property_objects)

        return super().update(instance, validated_data)


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

    def update(self, instance: Any, validated_data: Any) -> Any:
        pickup_address = validated_data.pop("pickup_address", None)
        lockbox = validated_data.pop("lockbox", None)
        if pickup_address:
            PropertySerializer(context={"request": self.request}).update(
                instance.pickup_address,
                validated_data=pickup_address,
            )
        if lockbox:
            if instance.lockbox:
                LockBoxSerializer().update(instance.lockbox, validated_data=lockbox)
            else:
                instance.lockbox = LockBoxSerializer().create(validated_data=lockbox)
                instance.save()

        return super().update(instance, validated_data)


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

    def update(self, instance: Any, validated_data: Any) -> Any:
        installation_or_remove_address = validated_data.pop(
            "installation_or_remove_address",
            None,
        )
        pickup_address = validated_data.pop("pickup_address", None)
        lockbox = validated_data.pop("lockbox", None)

        if installation_or_remove_address:
            PropertySerializer(context={"request": self.request}).update(
                instance.installation_or_remove_address,
                installation_or_remove_address,
            )
        if pickup_address:
            PropertySerializer(context={"request": self.request}).update(
                instance.pickup_address,
                pickup_address,
            )
        if lockbox:
            if instance.lockbox:
                LockBoxSerializer().update(instance.lockbox, lockbox)
            else:
                LockBoxSerializer().create(lockbox)

        return super().update(instance, validated_data)


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

    def update(self, instance: Any, validated_data: Any) -> Any:
        property_address = validated_data.pop("property_address", None)
        if property_address:
            PropertySerializer(context={"request": self.request}).update(
                instance.property_address,
                property_address,
            )
        return super().update(instance, validated_data)


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

    def update(self, instance: Any, validated_data: Any) -> Any:
        property_address = validated_data.pop("property_address", None)
        if property_address:
            PropertySerializer(context={"request": self.request}).update(
                instance.property_address,
                property_address,
            )
        return super().update(instance, validated_data)


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

    def validate(self, attrs: Any) -> Any:
        if self.request._request.method == "POST":  # noqa: SLF001
            task_type = attrs["task_type"]
            if task_type == SignTaskType.install:
                if not all([attrs.get("install_address"), attrs.get("pickup_address")]):
                    msg = "when task_type is install.\
                          the install_address and pickup_address is required."
                    raise serializers.ValidationError(msg, code="address")

            if task_type == SignTaskType.remove:
                if not all([attrs.get("remove_address"), attrs.get("dropoff_address")]):
                    msg = """when task_type is install or remove,
                            the remove_address and dropoff_address are required."""
                    raise serializers.ValidationError(msg, code="address")
        return super().validate(attrs)

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
            instance.save(update_fields=["pickup_address", "install_address"])

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
            instance.save(update_fields=["dropoff_address", "remove_address"])
        return instance

    def to_representation(self, instance: Any) -> dict[str, Any]:
        rep = super().to_representation(instance)
        if instance.task_type == "INSTALL":
            rep.pop("remove_address", None)
            rep.pop("dropoff_address", None)

        if instance.task_type == "REMOVE":
            rep.pop("install_address", None)
            rep.pop("pickup_address", None)
        return rep

    def update(self, instance: Any, validated_data: Any) -> Any:
        install_address = validated_data.pop("install_address", None)
        pickup_address = validated_data.pop("pickup_address", None)
        remove_address = validated_data.pop("remove_address", None)
        dropoff_address = validated_data.pop("dropoff_address", None)

        if install_address and (ia_object := instance.install_address):
            PropertySerializer(context={"request": self.request}).update(
                ia_object,
                install_address,
            )
        if pickup_address and (pa_object := instance.pickup_address):
            PropertySerializer(context={"request": self.request}).update(
                pa_object,
                pickup_address,
            )
        if remove_address and (ra_object := instance.remove_address):
            PropertySerializer(context={"request": self.request}).update(
                ra_object,
                remove_address,
            )
        if dropoff_address and (da_object := instance.dropoff_address):
            PropertySerializer(context={"request": self.request}).update(
                da_object,
                dropoff_address,
            )
        return super().update(instance, validated_data)


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
        data["open_for_vendor"] = VendorTypeSerializer(
            instance.open_for_vendor.all(),
            many=True,
        ).data
        return data

    class Meta(TaskSerializer.Meta):
        model = OpenForVendorTask
        fields = "__all__"

    def create(self, validated_data: Any) -> Any:
        property_address = validated_data.pop("property_address", None)
        instance = super().create(validated_data)

        properties = self.save_property_instance(
            task=instance,
            request=self.request,
            property_validated_data=property_address,
            many=True,
        )
        instance.property_address.set(properties)
        return instance

    def update(self, instance: Any, validated_data: Any) -> Any:
        property_addresses = validated_data.pop("property_address", [])
        property_objects = list(instance.property_address.all())
        if property_addresses:
            for address in property_addresses:
                is_delete = address.pop("delete", False)
                if property_id := address.get("id", None):
                    try:
                        property_instance = Property.objects.get(id=property_id)
                    except Property.DoesNotExist:
                        raise PropertyNotFound(property_id=property_id) from None

                    if not is_delete:
                        PropertySerializer().update(property_instance, address)

                    else:
                        property_instance.delete()
                else:
                    property_objects.append(
                        self.save_property_instance(
                            task=instance,
                            request=self.request,
                            property_validated_data=address,
                            many=False,
                        ),
                    )

            instance.property_address.set(property_objects)

        return super().update(instance, validated_data)


class JobCreaterDashboardSerializer(serializers.Serializer):
    Showing = ShowingTaskSerializer(
        many=True,
        fields=JOB_CREATER_FIELDS["SHOWING"],
        required=False,
    )
    Sign = SignTaskSerializer(
        many=True,
        fields=JOB_CREATER_FIELDS["SIGN"],
        required=False,
    )
    Runner = RunnerTaskSerializer(
        many=True,
        fields=JOB_CREATER_FIELDS["RUNNER"],
        required=False,
    )
    Professional = ProfessionalTaskSerializer(
        many=True,
        fields=JOB_CREATER_FIELDS["PROFESSIONAL"],
        required=False,
    )
    OpenHouse = OpenHouseTaskSerializer(
        many=True,
        fields=JOB_CREATER_FIELDS["OPENHOUSE"],
        required=False,
    )
    LockBoxIR = LockBoxBSSerializer(
        many=True,
        fields=JOB_CREATER_FIELDS["LOCKBOXBS"],
        required=False,
    )
    LockBoxBS = LockBoxIRSerializer(
        many=True,
        fields=JOB_CREATER_FIELDS["LOCKBOXIR"],
        required=False,
    )

    OpenForVendor = OpenForVendorTaskSerializer(
        many=True,
        fields=JOB_CREATER_FIELDS["OPENFORVENDOR"],
        required=False,
    )


class JobSeekerDashboardSerializer(serializers.Serializer):
    Showing = ShowingTaskSerializer(
        many=True,
        fields=JOB_SEEKER_FIELDS["SHOWING"],
        required=False,
    )
    Sign = SignTaskSerializer(
        many=True,
        fields=JOB_SEEKER_FIELDS["SIGN"],
        required=False,
    )
    Runner = RunnerTaskSerializer(
        many=True,
        fields=JOB_SEEKER_FIELDS["RUNNER"],
        required=False,
    )
    Professional = ProfessionalTaskSerializer(
        many=True,
        fields=JOB_SEEKER_FIELDS["PROFESSIONAL"],
        required=False,
    )
    OpenHouse = OpenHouseTaskSerializer(
        many=True,
        fields=JOB_SEEKER_FIELDS["OPENHOUSE"],
        required=False,
    )
    LockBoxIR = LockBoxBSSerializer(
        many=True,
        fields=JOB_SEEKER_FIELDS["LOCKBOXBS"],
        required=False,
    )
    LockBoxBS = LockBoxIRSerializer(
        many=True,
        fields=JOB_SEEKER_FIELDS["LOCKBOXIR"],
        required=False,
    )

    OpenForVendor = OpenForVendorTaskSerializer(
        many=True,
        fields=JOB_SEEKER_FIELDS["OPENFORVENDOR"],
        required=False,
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
