import logging
import uuid

from django.utils.timezone import now
from paypalrestsdk import Payout

_logger = logging.getLogger(__name__)


def create_payment():
    batch_id = f"batch-{now()!s}"
    payout = Payout(
        {
            "sender_batch_header": {
                "sender_batch_id": batch_id,
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


def process_payments():
    # Prepare items for batch payout
    payout_items = []

    payout_items.extend(
        [
            {
                "recipient_type": "EMAIL",
                "amount": {"value": str(10), "currency": "USD"},
                "receiver": "a@a.com",  # Assignee's email
                "note": "Payment for Task Hello",
                "sender_item_id": str(uuid.uuid4()),  # Unique item id for tracking
            },
            {
                "recipient_type": "EMAIL",
                "amount": {"value": str(10), "currency": "USD"},
                "receiver": "sb-kki14731829447@personal.example.com",  # Assignee's email
                "note": "Payment for Task Hello",
                "sender_item_id": str(uuid.uuid4()),  # Unique item id for tracking
            },
        ],
    )

    # If there are no payments to process, return
    if not payout_items:
        return

    try:
        payout = Payout.find()
        # Send the batch request
        payout = Payout(
            {
                "sender_batch_header": {
                    "sender_batch_id": f"batch_{now()!s}",  # Unique batch id
                    "email_subject": "You have a payment",
                },
                "items": payout_items,
            },
        )

        if payout:
            # Process successful payout
            handle_successful_payout(payout)
        else:
            # Handle failure case
            handle_failed_payout(payout.error)

    except Exception:  # noqa: BLE001, S110
        pass


def handle_successful_payout(payout):
    """
    Handle the response for a successful payout and update the payment history.
    """
    # Go through each payment and update with success status and transaction


def handle_failed_payout(error_message):
    """
    Handle the response for a failed payout and update the payment history.
    """
