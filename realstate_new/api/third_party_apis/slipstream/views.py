from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from realstate_new.master.models import Property

from .slipstream import SlipStreamApi


class ZipCodeDetailView(APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        response = SlipStreamApi().get_zipcode_details([90210])
        return Response(response.json(), response.status_code)


class AgentAssignedAddressView(APIView):
    class MLSIDSerializer(serializers.Serializer):
        mls_id = serializers.IntegerField()

    serializer_class = MLSIDSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            response = SlipStreamApi().get_agent_assigned_properties(
                mls_id=serializer.validated_data.get("mls_id", None),
            )

            if response.status_code == status.HTTP_200_OK:
                Property.objects.create(
                    api_response=response.json(),
                )
            return Response({"status": True}, response.status_code)
