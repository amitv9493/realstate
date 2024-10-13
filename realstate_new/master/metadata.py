from copy import deepcopy
from typing import TypedDict


class FieldDataType(TypedDict):
    id: str
    label: str
    required: bool
    dataType: str
    defaultValue: None | str
    fields: list | None
    readOnly: bool


class TaskMetaData(TypedDict):
    type: str
    child: str
    fields: list | None


class MetaData:
    def get_field_type(  # noqa: PLR0913
        self,
        id,  # noqa: A002
        label,
        data_type,
        default_value: str | None = None,
        fields: list | None = None,
        required=False,  # noqa: FBT002
        read_only=False,  # noqa: FBT002
    ):
        data: FieldDataType = {
            "id": id,
            "label": label,
            "dataType": data_type,
            "defaultValue": default_value,
            "fields": fields,
            "required": required,
            "readOnly": read_only,
        }
        return data

    @property
    def task_type(self):
        return self.get_field_type(
            id="taskType",
            label="Task Type",
            data_type="String",
        )

    @property
    def ongoing_showing_task_metadata(self):
        _data: TaskMetaData = {
            "type": "task",
            "child": "Showing",
            "fields": self.common_task_metadata,
        }
        return _data

    @property
    def ongoing_sign_task_metadata(self):
        _data = self.common_task_metadata
        _data.append(self.task_type)
        extra_fields = [
            self.get_field_type(
                id="dropoffAddress",
                label="Dropoff Address",
                data_type="Object",
            ),
            self.get_field_type(
                id="installAddress",
                label="Install Address",
                data_type="Object",  # Assuming this is a related object reference
            ),
            self.get_field_type(
                id="pickupAddress",
                label="Pickup Address",
                data_type="Object",
            ),
            self.get_field_type(
                id="removeAddress",
                label="Remove Address",
                data_type="Object",
            ),
            self.task_type,
        ]
        _data.extend(extra_fields)
        list_data: TaskMetaData = {
            "type": "task",
            "child": "Sign",
            "fields": _data,
        }
        return list_data

    @property
    def ongoing_runner_task_metadata(self):
        _data = self.common_task_metadata
        _data.append(self.task_type)
        list_data: TaskMetaData = {
            "type": "task",
            "child": "Runner",
            "fields": _data,
        }
        return list_data

    @property
    def ongoing_openhouse_task_metadata(self):
        _data = self.common_task_metadata
        list_data: TaskMetaData = {
            "type": "task",
            "child": "OpenHouse",
            "fields": _data,
        }
        return list_data

    @property
    def ongoing_lockbox_bs_task_metadata(self):
        _data = self.common_task_metadata
        _data.append(self.task_type)
        for idx, i in enumerate(_data):
            if i["id"] == "property":
                _data.pop(idx)
                break

        pickup_address = {
            "id": "pickupAddress",
            "label": "Pickup Address",
            "dataType": "Object",
            "defaultValue": None,
            "required": True,
            "fields": self.property_metadata,
        }
        _data.append(pickup_address)

        return {"type": "task", "child": "LockBoxBS", "fields": _data}

    @property
    def ongoing_lockbox_ir_task_metadata(self):
        _data = self.common_task_metadata
        for idx, i in enumerate(_data):
            if i["id"] == "property":
                _data.pop(idx)
                break
        extra_fields = [
            self.task_type,
            self.get_field_type(
                id="pickupAddress",
                label="Pickup Address",
                data_type="Object",
                fields=self.property_metadata,
            ),
            self.get_field_type(
                id="installationOrRemoveAddress",
                label="Installation/Remove Address",
                data_type="Object",
                fields=self.property_metadata,
            ),
        ]
        _data.extend(extra_fields)

        return {"type": "task", "child": "LockBoxIR", "fields": _data}

    @property
    def ongoing_task_metadata(self):
        return [
            self.ongoing_showing_task_metadata,
            self.ongoing_sign_task_metadata,
            self.ongoing_runner_task_metadata,
            self.ongoing_openhouse_task_metadata,
            self.ongoing_lockbox_bs_task_metadata,
            self.ongoing_lockbox_ir_task_metadata,
        ]

    @property
    def ongoing_professional_task_metadata(self):
        _data = self.common_task_metadata
        service_type: FieldDataType = {
            "id": "serviceType",
            "dataType": "String",
            "defaultValue": None,
            "fields": None,
            "label": "Service Type",
            "required": True,
        }
        _data.append(service_type)
        return {"type": "task", "child": "LockBoxBS", "fields": _data}

    @property
    def ongoing_runner_metadata(self):
        _data = self.common_task_metadata

        return {"type": "task", "child": "Runner", "fields": _data}

    @property
    def property_metadata(self):
        return [
            {
                "id": "city",
                "label": "City",
                "required": True,
                "dataType": "String",
                "defaultValue": None,
            },
            {
                "id": "state",
                "label": "State",
                "required": True,
                "dataType": "String",
                "defaultValue": None,
            },
            {
                "id": "zip",
                "label": "ZIP Code",
                "required": True,
                "dataType": "String",
                "defaultValue": None,
            },
            {
                "id": "street",
                "label": "Street",
                "required": True,
                "dataType": "String",
                "defaultValue": None,
            },
            {
                "id": "latitude",
                "label": "Latitude",
                "required": True,
                "dataType": "String",
                "defaultValue": None,
            },
            {
                "id": "longitude",
                "label": "Longitude",
                "required": True,
                "dataType": "String",
                "defaultValue": None,
            },
        ]

    @property
    def common_task_metadata(self):
        return [
            self.get_field_type(
                id="id",
                label="Task ID",
                data_type="Integer",
                default_value=None,
                required=False,
                read_only=True,
            ),
            self.get_field_type(
                id="typeOfTask",
                label="Job Type",
                data_type="String",
                default_value="Showing",
                required=False,
                read_only=True,
            ),
            self.get_field_type(
                id="property",
                label="Property Details",
                data_type="Object",
                default_value=None,
                fields=self.property_metadata,
                required=True,
                read_only=False,
            ),
            self.get_field_type(
                id="taskTime",
                label="Task Time",
                data_type="DateTime",
                default_value=None,
                required=True,
                read_only=False,
            ),
            self.get_field_type(
                id="paymentAmount",
                label="Payment Amount",
                data_type="Decimal",
                default_value=None,
                required=True,
                read_only=False,
            ),
            self.get_field_type(
                id="applicationType",
                label="Application Type",
                data_type="String",
                default_value=None,
                required=True,
                read_only=False,
            ),
            self.get_field_type(
                id="createdBy",
                label="Created By",
                data_type="Integer",
                default_value=None,
                required=False,
                read_only=True,
            ),
            self.get_field_type(
                id="assignedTo",
                label="Assigned To",
                data_type="Object",
                default_value=None,
                fields=self.user_metadata,
                required=False,
                read_only=True,
            ),
            self.get_field_type(
                id="status",
                label="status",
                data_type="String",
                read_only=True,
            ),
            self.get_field_type(
                "asap",
                "ASAP",
                "Boolean",
            ),
            self.get_field_type(
                id="vacant",
                label="Vacant",
                data_type="Boolean",
            ),
            self.get_field_type(
                id="pets",
                label="Pets",
                data_type="Boolean",
            ),
            self.get_field_type(
                id="concierge",
                label="Concierge",
                data_type="Boolean",
            ),
            self.get_field_type(
                id="alarmCode",
                label="Alarm Code",
                data_type="String",
            ),
            self.get_field_type(
                id="gateCode",
                label="Gate Code",
                data_type="String",
            ),
            self.get_field_type(
                id="lockboxType",
                label="Lockbox Type",
                data_type="String",
            ),
        ]

    @property
    def user_metadata(self):
        return [
            {
                "id": "username",
                "label": "Username",
                "type": "string",
                "required": True,
                "defaultValue": "",
                "readonly": False,
            },
            {
                "id": "firstName",
                "label": "First Name",
                "type": "string",
                "required": True,
                "defaultValue": "",
                "readonly": False,
            },
            {
                "id": "lastName",
                "label": "Last Name",
                "type": "string",
                "required": True,
                "defaultValue": "",
                "readonly": False,
            },
            {
                "id": "email",
                "label": "Email",
                "type": "string",
                "required": True,
                "defaultValue": "",
                "readonly": False,
            },
            {
                "id": "phone",
                "label": "Phone",
                "type": "string",
                "required": False,
                "defaultValue": "",
                "readonly": True,
            },
        ]

    @property
    def common_post_task_metadata(self):
        _data = self.common_task_metadata
        _data = self.remove_items(_data, ["assignedTo", "createdBy"])

        extra_fields = [
            self.get_field_type(
                id="clientPhone",
                label="Client Phone",
                data_type="String",
            ),
            self.get_field_type(
                "asap",
                "ASAP",
                "Boolean",
            ),
            self.get_field_type(
                id="clientName",
                label="Client Name",
                data_type="String",
            ),
            self.get_field_type(
                id="lockboxType",
                label="Lockbox Type",
                data_type="String",
            ),
            self.get_field_type(
                id="audioFile",
                label="Audio File",
                data_type="File",
            ),
            self.get_field_type(
                id="vacant",
                label="Vacant",
                data_type="Boolean",
            ),
            self.get_field_type(
                id="pets",
                label="Pets",
                data_type="Boolean",
            ),
            self.get_field_type(
                id="concierge",
                label="Concierge",
                data_type="Boolean",
            ),
            self.get_field_type(
                id="alarmCode",
                label="Alarm Code",
                data_type="String",
            ),
            self.get_field_type(
                id="gateCode",
                label="Gate Code",
                data_type="String",
            ),
            self.get_field_type(
                id="notes",
                label="Additional Notes",
                data_type="String",
            ),
        ]
        _data.extend(extra_fields)
        return _data

    @property
    def post_showing_metadata(self):
        return self.common_post_task_metadata

    @property
    def post_openhouse_metadata(self):
        _data = self.common_post_task_metadata
        extra_fields = [
            self.get_field_type(
                id="listingAgent",
                label="Listing Agent",
                data_type="Boolean",
            ),
            self.get_field_type(
                id="hostingAgent",
                label="Hosting Agent",
                data_type="Boolean",
            ),
        ]
        _data.extend(extra_fields)
        return _data

    def remove_items(self, data: list[dict], items: list):
        _data_copy = deepcopy(data)
        for idx, obj in enumerate(data):
            for item in items:
                if obj["id"] == item:
                    _data_copy.pop(idx)

        return _data_copy

    @property
    def post_lockbox_ir_metadata(self):
        _data = self.common_post_task_metadata
        _data = self.remove_items(_data, ["property"])

        extra_fields = [
            self.task_type,
            self.get_field_type(
                id="pickupAddress",
                label="Pickup Address",
                data_type="Object",
                fields=self.property_metadata,
            ),
            self.get_field_type(
                id="installationOrRemoveAddress",
                label="Installation/Remove Address",
                data_type="Object",
                fields=self.property_metadata,
            ),
            self.get_field_type(
                id="includeSign",
                label="Include Sign",
                data_type="Boolean",
            ),
            self.get_field_type(
                id="removeSign",
                label="Remove Sign",
                data_type="Boolean",
            ),
        ]
        _data.extend(extra_fields)
        return _data

    @property
    def post_lockbox_bs_metadata(self):
        _data = self.post_lockbox_ir_metadata
        return self.remove_items(_data, items=["installationOrRemoveAddress"])

    @property
    def post_sign_metadata(self):
        _data = self.common_post_task_metadata

        extra_fields = [
            self.get_field_type(
                id="installAddress",
                label="Install Address",
                data_type="Object",
                fields=self.property_metadata,
            ),
            self.get_field_type(
                id="pickupAddress",
                label="Pickup Address",
                data_type="Object",
                fields=self.property_metadata,
            ),
            self.get_field_type(
                id="removeAddress",
                label="Remove Address",
                data_type="Object",
                fields=self.property_metadata,
            ),
            self.get_field_type(
                id="dropoffAddress",
                label="Dropoff Address",
                data_type="Object",
                fields=self.property_metadata,
            ),
            self.get_field_type(
                id="signType",
                label="Sign Type",
                data_type="String",
            ),
            self.get_field_type(
                id="instructions",
                label="Instructions",
                data_type="String",
            ),
            self.task_type,
        ]

        _data.extend(extra_fields)
        return _data

    @property
    def post_runner_metadata(self):
        _data = self.common_post_task_metadata
        extra_fields = [
            self.get_field_type(
                id="instructions",
                label="Instructions",
                data_type="String",
            ),
            self.task_type,
        ]
        _data.extend(extra_fields)
        return _data

    @property
    def post_professional_metadata(self):
        _data = self.common_post_task_metadata
        extra_fields = [
            self.get_field_type(
                id="serviceType",
                label="Service Type",
                data_type="String",
            ),
            self.get_field_type(
                id="name",
                label="Name",
                data_type="String",
            ),
            self.get_field_type(
                id="companyName",
                label="Company Name",
                data_type="String",
            ),
            self.get_field_type(
                id="phone",
                label="Phone",
                data_type="String",
            ),
            self.get_field_type(
                id="email",
                label="Email",
                data_type="String",
            ),
            self.get_field_type(
                id="address",
                label="Address",
                data_type="String",
            ),
            self.get_field_type(
                id="website",
                label="Website",
                data_type="String",
            ),
        ]
        _data.extend(extra_fields)
        return _data

    def get_metadata_list(self, type, child, fields):  # noqa: A002
        return {
            "type": type,
            "child": child,
            "fields": fields,
        }
