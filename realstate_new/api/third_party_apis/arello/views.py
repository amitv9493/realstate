from rest_framework.response import Response
from rest_framework.views import APIView

from .arello import ArelloService


class ArelloView(APIView):
    serializer_class = None

    def post(self, request):
        response = ArelloService().get_license_info(request.user)
        data = response.json()
        return Response(data, response.status_code)
