from rest_framework.response import Response
from rest_framework.views import APIView

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
            return Response({"msg": "Updated", "status": True}, 200)
