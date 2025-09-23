import logging
from typing import Annotated

import stripe
from fastapi import APIRouter, Depends
from fastapi.requests import Request

from src.base.dependencies import get_service
from src.payment.services.webhooks import StripeWebhookService
from src.settings import Settings

settings = Settings.load()

logger = logging.getLogger(__name__)

webhooks_payment_router = APIRouter()


@webhooks_payment_router.post('/stripe')
async def stripe_webhook(
    request: Request,
    service: Annotated[
        StripeWebhookService, Depends(get_service(StripeWebhookService))
    ],
) -> None:
    """Handle incoming Stripe webhook events.

    This endpoint processes webhook notifications from Stripe, verifies their
    signature, and delegates the event handling to the webhook service.

    Args:
        request (Request): The incoming FastAPI request containing the webhook
            payload and headers.
        service (StripeWebhookService): Service for processing Stripe webhook
            events.

    Returns:
        None

    """
    request_body: bytes = await request.body()
    stripe_signature = request.headers['stripe-signature']
    stripe.Webhook.construct_event(
        request_body,
        stripe_signature,
        settings.stripe_settings.WEBHOOK_SECRET_KEY,
    )
    await service.handle_webhook(request_body=request_body)
