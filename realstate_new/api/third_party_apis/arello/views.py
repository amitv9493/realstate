from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .arello import ArelloService


class ArelloView(APIView):
    serializer_class = None

    def post(self, request):
        response = ArelloService().get_license_info(request.user)
        data = response.json()
        if response.status_code == status.HTTP_200_OK:
            return Response({"results": data["results"]}, response.status_code)

        return Response({"msg": "Some error occured while calling the third party api"})
