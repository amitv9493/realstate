from django.contrib.auth import get_user_model

from realstate_new.utils.serializers import DynamicModelSerializer


class UserSerializer(DynamicModelSerializer):
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
