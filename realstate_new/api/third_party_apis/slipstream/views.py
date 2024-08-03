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

    def post(self, request, *args, **kwargs):
        license_number = request.user.license_number
        license_jurisdiction = request.user.license_jurisdiction

        if not license_number or not license_jurisdiction:
            return Response(
                {"error": "license number and license jurisdiction is not saved"},
                400,
            )

        # using dummy query param as of now
        response = SlipStreamApi().get_agent_assigned_properties(
            license_number,
            license_jurisdiction,
        )
        return Response(response.json(), response.status_code)
