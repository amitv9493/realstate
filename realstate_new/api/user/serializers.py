from django.contrib.auth import get_user_model
from rest_framework import fields

from realstate_new.users.models import DAYS_OF_WEEK
from realstate_new.users.models import JOB_TYPES
from realstate_new.users.models import ProfessionalDetail
from realstate_new.utils.serializers import DynamicModelSerializer


class UserSerializer(DynamicModelSerializer):
    job_preferences = fields.MultipleChoiceField(choices=JOB_TYPES)
    days_of_week_preferences = fields.MultipleChoiceField(choices=DAYS_OF_WEEK)

    class Meta:
        model = get_user_model()
        fields = "__all__"
        exclude_fields = [
            "password",
            "groups",
            "user_permissions",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
        ]


class UserMeSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = "__all__"


class ProfessionalDetailSerializer(DynamicModelSerializer):
    class Meta:
        fields = "__all__"
        model = ProfessionalDetail
        exclude_fields = ["user"]
        extra_kwargs = {"created_by": {"read_only": True}}
