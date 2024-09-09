from rest_framework.viewsets import ModelViewSet

from realstate_new.task.models import ShowingTask
from realstate_new.users.models import User

from .serializers import ShowingTaskSerializer


class ShowingTaskViewSet(ModelViewSet):
    serializer_class = ShowingTaskSerializer
    queryset = ShowingTask.objects.all()

    def perform_create(self, serializer):
        amount = serializer.validated_data["payment_amount"]
        self.request.user.wallet.deduct_amount(amount)
        serializer.validated_data["created_by"] = self.request.user
        return super().perform_create(serializer)


def get_user_preferences(user: User):
    return user.days_of_week_preferences
