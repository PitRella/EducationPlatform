from fastapi import APIRouter
from fastapi.requests import Request
import stripe
import logging

from src.settings import Settings

settings = Settings.load()
from src.payment.services.webhooks import StripeWebhookService

logger = logging.getLogger(__name__)

webhooks_payment_router = APIRouter()


@webhooks_payment_router.post("/stripe")
async def stripe_webhook(request: Request) -> None:
    request_body: bytes = await request.body()
    stripe_signature = request.headers['stripe-signature']
    stripe.Webhook.construct_event(
        body,stripe_signature,settings.stripe_settings.WEBHOOK_SECRET_KEY
    )
    await StripeWebhookService.handle_webhook(request_body=request_body)

