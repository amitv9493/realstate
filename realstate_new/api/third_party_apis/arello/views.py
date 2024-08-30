from rest_framework.response import Response
from rest_framework.views import APIView

from .arello import ArelloService
from .serializers import ArelloSerializer


class ArelloView(APIView):
    serializer_class = ArelloSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):  # noqa: RET503
            response = ArelloService().get_license_info(serializer.validated_data)
            data = response.json()

            if len(results := data.get("results", [])):
                return Response({"results": results}, response.status_code)

            if len(errors := data.get("errors", [])):
                error_list = [error["error"] for error in errors]
                if "InvalidJurisdiction" in error_list:
                    error_msg = "Invalid Jurisdiction"

                return Response({"msg": error_msg})
            return Response({"msg": "Invalid License Number."}, 400)
