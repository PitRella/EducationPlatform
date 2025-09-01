from fastapi import APIRouter
from fastapi.requests import Request
import logging

logger = logging.getLogger(__name__)

webhooks_payment_router = APIRouter()


@webhooks_payment_router.post("/stripe")
async def stripe_webhook(request: Request) -> None:
    logger.info("Received a webhook from stripe")
    payload = await request.body()
    logger.info(f"Payload: %s", payload)
