import stripe
from src.payment.dto import StripeWebhookPayload


class StripeWebhookService:
    @classmethod
    async def handle_webhook(
            cls,
            request_body: bytes
    ):
        payload: StripeWebhookPayload = StripeWebhookPayload.from_body(request_body)

