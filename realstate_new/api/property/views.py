from rest_framework.viewsets import ModelViewSet

from realstate_new.master.models import Property

from .serializers import PropertySerializer


class PropertyViewSet(ModelViewSet):
    serializer_class = PropertySerializer
    queryset = Property.objects.all()
    http_method_names = (
        "get",
        "patch",
        "put",
        "delete",
    )
