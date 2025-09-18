from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
import stripe
import logging

from src.base.dependencies import get_service
from src.settings import Settings

settings = Settings.load()
from src.payment.services.webhooks import StripeWebhookService

logger = logging.getLogger(__name__)

webhooks_payment_router = APIRouter()


@webhooks_payment_router.post("/stripe")
async def stripe_webhook(
        request: Request,
        service: Annotated[
            StripeWebhookService, Depends(get_service(StripeWebhookService))],
) -> None:
    request_body: bytes = await request.body()
    stripe_signature = request.headers['stripe-signature']
    stripe.Webhook.construct_event(
        request_body,
        stripe_signature,
        settings.stripe_settings.WEBHOOK_SECRET_KEY
    )
    await service.handle_webhook(request_body=request_body)
