import stripe
from src.payment.dto import StripeWebhookPayload


class StripeWebhookService:
    @classmethod
    async def handle_webhook(cls, body: bytes):
        payload: StripeWebhookPayload = StripeWebhookPayload.from_body(body)
