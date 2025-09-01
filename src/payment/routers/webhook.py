from fastapi import APIRouter
from fastapi.requests import Request
import logging

from src.payment.services.webhooks import StripeWebhookService

logger = logging.getLogger(__name__)

webhooks_payment_router = APIRouter()


@webhooks_payment_router.post("/stripe")
async def stripe_webhook(request: Request) -> None:
    body: bytes = await request.body()
    await StripeWebhookService.handle_webhook(body)

