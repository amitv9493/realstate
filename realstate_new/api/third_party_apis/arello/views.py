from rest_framework.response import Response
from rest_framework.views import APIView

from .arello import ArelloService
from .serializers import ArelloSerializer


class ArelloView(APIView):
    serializer_class = ArelloSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = ArelloService().get_license_info(serializer.validated_data)
            data = response.json()
            if len(results := data.get("results", [])):
                return Response({"results": results}, response.status_code)

        return Response({"msg": "Some error occured while calling the third party api"})
