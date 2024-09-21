from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .slipstream import SlipStreamApi


class ZipCodeDetailView(APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        response = SlipStreamApi().get_zipcode_details([90210])
        return Response(response.json(), response.status_code)


class AgentAssignedAddressView(APIView):
    serializer_class = None

    def get(self, request, mls_id, *args, **kwargs):
        response = SlipStreamApi().get_agent_assigned_properties(
            mls_id=mls_id,
        )

        if response.status_code == status.HTTP_200_OK:
            cleaned_response = response.json()["result"]["listings"]
            return Response(cleaned_response, response.status_code)
        raise serializers.ValidationError(msg=response.json(), code="client_error")
