from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from realstate_new.master.models import Property

from .serializers import PropertyCreateSerializer
from .serializers import PropertySerializer


class PropertyViewSet(ModelViewSet):
    serializer_class = PropertySerializer
    queryset = Property.objects.all()


class PropertyCreateView(APIView):
    serilaizer_class = PropertyCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serilaizer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            serializer.save()
            return Response({"status": True}, 200)
