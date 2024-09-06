from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from .serializers import UserMeSerializer
from .serializers import UserSerializer


class UserView(APIView):
    serializer_class = UserSerializer

    def patch(self, request):
        serializer = self.serializer_class(
            request.user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            serializer.save()
            return Response({"msg": serializer.validated_data, "status": True}, 200)


class UserMeView(APIView):
    serializer_class = UserMeSerializer
    basic = [
        "last_login",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "date_joined",
        "job_preferences",
        "time_preference_start",
        "time_preference_end",
        "days_of_week_preferences",
        "mile_radius_preference",
        "phone",
        "phone_country_code",
    ]
    preferences = [
        "job_preferences",
        "time_preference_start",
        "time_preference_end",
        "days_of_week_preferences",
        "mile_radius_preference",
    ]
    license = [
        "license_number",
        "license_issue_date",
        "license_expiration_date",
        "license_status",
        "license_type",
        "license_jurisdiction",
        "suffix",
        "office_name",
        "address_line1",
        "address_line2",
        "city",
        "state_province",
        "postal_code",
        "country",
    ]

    def get(self, request, *args, **kwargs):
        details = request.query_params.get("details")
        user = request.user
        data = {}
        if details:
            details = details.split(",")
            for detail in details:
                if detail == "basic":
                    data["basic"] = self.serializer_class(user, fields=self.basic).data
                elif detail == "preferences":
                    data["preferences"] = self.serializer_class(
                        user,
                        fields=self.preferences,
                    ).data
                elif detail == "license":
                    data["license"] = self.serializer_class(
                        user,
                        fields=self.license,
                    ).data
        else:
            msg = "please provide details query params options are 'basic' 'license' 'preferences'"
            raise ValidationError(msg)
        return Response(data, 200)
