from rest_framework.generics import CreateAPIView

from .serializers import FeedbackSerializer
from .serializers import ProfessionalInquirySerializer


class ProfessionalInquiryView(CreateAPIView):
    serializer_class = ProfessionalInquirySerializer

    def perform_create(self, serializer) -> None:
        return super().perform_create(serializer)


class FeedbackView(CreateAPIView):
    serializer_class = FeedbackSerializer
