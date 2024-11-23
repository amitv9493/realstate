from django.db.models.query import QuerySet
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from realstate_new.users.models import ProfessionalDetail
from realstate_new.users.models import User

from .serializers import ProfessionalDetailSerializer
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
            return Response({"status": True}, 200)


class UserMeView(APIView):
    serializer_class = UserMeSerializer

    def get(self, request, *args, **kwargs):
        details = request.query_params.get("details")
        user: User = request.user
        data = {}
        if details:
            details = details.split(",")
            for detail in details:
                if detail == "basic":
                    data["basic"] = user.basic_info
                    if profile_picture := user.basic_info["profile_picture"]:
                        data["basic"]["profile_picture"] = request.build_absolute_uri(
                            profile_picture.url,
                        )
                    else:
                        data["basic"]["profile_picture"] = ""
                elif detail == "preferences":
                    data["preferences"] = user.preferences
                elif detail == "license":
                    data["license"] = user.license_info
        else:
            msg = "please provide `details` query params.\
                    Options are 'basic' 'license' 'preferences'"

            raise ValidationError(msg)
        return Response(data, 200)


class ProfessionalDetailViewSet(ModelViewSet):
    serializer_class = ProfessionalDetailSerializer
    queryset = ProfessionalDetail.objects.all()

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        return qs.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer) -> None:
        serializer.validated_data["user"] = self.request.user
        serializer.validated_data["created_by"] = self.request.user
        return super().perform_create(serializer)


def test_logs(request):
    x = 5
    x.upper()
    return HttpResponse("error", 400)
