from fastapi.requests import Request

from src.payment.dto import StripeWebhookPayload


class StripeWebhookService:
    async def handle_webhook(self, body: bytes):
        payload = StripeWebhookPayload.from_body(body)