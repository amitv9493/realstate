import logging
import time
from urllib.parse import urljoin

from hyperwallet import Api
from hyperwallet.utils.apiclient import ApiClient

from config.settings.base import env
from realstate_new.payment.models import PaymentStatusChoices
from realstate_new.payment.models import Transcation
from realstate_new.payment.models.choices import PaymentTypeChoics

logger = logging.getLogger(__name__)


class CustomApiClient(ApiClient):
    def __init__(self, username, password, server, encryptionData=None):  # noqa: N803
        super().__init__(username, password, server, encryptionData)
        self.baseUrl = urljoin(self.server, "/rest/v4/")


class CustomApi(Api):
    def __init__(
        self,
        username=None,
        password=None,
        programToken=None,  # noqa: N803
        server=...,
        encryptionData=None,  # noqa: N803
    ):
        super().__init__(username, password, programToken, server, encryptionData)
        self.apiClient = CustomApiClient(
            self.username,
            self.password,
            self.server,
            encryptionData,
        )


class HyperwalletPayoutHandler:
    def __init__(self):
        self.program_token = env("HYPERWALLET_PROGRAM_TOKEN")
        self.api = CustomApi(
            username=env("HYPERWALLET_USERNAME"),
            password=env("HYPERWALLET_PASSWORD"),
            programToken=self.program_token,
            server=env("HYPERWALLET_URL"),
        )

    def create_payment(self, task, amount, currency="USD", purpose="OTHER"):
        """
        Create a payout to a user using Hyperwallet

        Args:
            user: Django User object
            amount: Decimal amount to pay
            currency: Currency code (default: USD)
            purpose: Payment purpose (default: task_completion)

        Returns:
            dict: Payment response from Hyperwallet
        """
        try:
            user = task.assigned_to
            user_token = self._get_user_token(user)

            payment_data = {
                "destinationToken": user_token,
                "clientPaymentId": f"pmt_{task.assigned_to.id}_{purpose}_{int(time.time())}",
                "amount": str(amount),
                "currency": currency,
                "purpose": purpose,
                "notes": f"Payment for {purpose}",
                "programToken": self.program_token,
            }

            # Create payment
            response = self.api.createPayment(payment_data)

            # Log successful payment
            msg = f"Payment created successfully for user {user.id} {amount}{currency}"

            logger.info(msg)
            Transcation.objects.create(
                content_object=task,
                user=user,
                transcation_id=response.token,
                status=PaymentStatusChoices.INITIATED,
                transcation_type=PaymentTypeChoics.PAYOUT,
            )
        except Exception:
            msg = "Payment failed for user id %d" % user.id
            logger.exception(msg)
            raise
        else:
            return response

    def _get_user_token(self, user):
        """
        Get or create Hyperwallet user token
        """
        if not user.hyperwallet_token:
            user_data = {
                "clientUserId": str(user.uuid),
                "profileType": "INDIVIDUAL",
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "city": "",
                "stateProvince": "",
                "country": "",
                "dateOfBirth": "",
                "addressLine1": "",
                "postalCode": "",
                "programToken": self.program_token,
            }

            try:
                response = self.api.createUser(user_data)
                user.hyperwallet_token = response.token
                user.save()
            except Exception:
                logger.exception("Failed to create Hyperwallet user")
                raise
            else:
                return response.token

        else:
            return user.hyperwallet_token

    def get_payment_status(self, payment_token):
        """
        Get the status of a payment
        """
        try:
            return self.api.getPayment(payment_token)
        except Exception:
            logger.exception("Failed to get payment status")
            raise
