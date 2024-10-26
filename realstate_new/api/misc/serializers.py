from realstate_new.master.models import Feedback
from realstate_new.master.models import ProfessioanlVendorInquiry
from realstate_new.utils.serializers import TrackingModelSerializer


class ProfessionalInquirySerializer(TrackingModelSerializer):
    class Meta:
        model = ProfessioanlVendorInquiry
        fields = "__all__"


class FeedbackSerializer(TrackingModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"
