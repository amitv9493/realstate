import logging
import uuid

from paypalrestsdk import Payout

_logger = logging.getLogger(__name__)


def create_payment():
    payout = Payout(
        {
            "sender_batch_header": {
                "sender_batch_id": str(uuid.uuid4()),  # str(datetime.today().date()),
                "email_subject": "You have a payment",
                "email_message": "You have received a payout! Thanks for using our service!",
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {"value": 10, "currency": "USD"},
                    "receiver": "sb-kki14731829447@personal.example.com",
                    "note": "Thank you.",
                },
            ],
        },
    )

    if payout.create():
        msg = f"payout {payout.batch_header.payout_batch_id} created successfully"
        _logger.info(
            msg,
        )
    else:
        _logger.error(payout.error)
        raise ValueError(msg=payout.error)
