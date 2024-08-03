from rest_framework.viewsets import ModelViewSet

from realstate_new.payment.tasks import start_create_payment
from realstate_new.task.models import ShowingTask

from .serializers import ShowingTaskSerializer


class TaskViewSet(ModelViewSet):
    serializer_class = ShowingTaskSerializer
    queryset = ShowingTask.objects.all()

    def perform_create(self, serializer):
        amount = serializer.validated_data["payment_amount"]
        self.request.user.wallet.deduct_amount(amount)
        serializer.validated_data["created_by"] = self.request.user
        return super().perform_create(serializer)

    def list(self, request, *args, **kwargs):
        start_create_payment.apply_async(countdown=20)
        return super().list(request, *args, **kwargs)
