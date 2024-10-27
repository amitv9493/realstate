from django.contrib.auth import get_user_model
from rest_framework import fields
from rest_framework import serializers

from realstate_new.users.models import DAYS_OF_WEEK
from realstate_new.users.models import JOB_TYPES
from realstate_new.users.models import ProfessionalDetail
from realstate_new.utils.serializers import DynamicModelSerializer
from realstate_new.utils.serializers import TrackingSerializer


class UserSerializer(DynamicModelSerializer):
    job_preferences = fields.MultipleChoiceField(choices=JOB_TYPES)
    days_of_week_preferences = fields.MultipleChoiceField(choices=DAYS_OF_WEEK)
    rating = serializers.SerializerMethodField()
    jobs_completed = serializers.SerializerMethodField()

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

    def get_rating(self, obj):
        return obj

    def get_jobs_completed(self, obj):
        count = 0
        for i in obj.get_jobs_completed_qs():
            count += i.count()
        return count


class UserMeSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = "__all__"


class ProfessionalDetailSerializer(TrackingSerializer):
    class Meta:
        fields = "__all__"
        model = ProfessionalDetail
        exclude_fields = ["user"]
        extra_kwargs = {"created_by": {"read_only": True}}
