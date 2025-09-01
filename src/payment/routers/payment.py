from typing import Annotated

from fastapi import APIRouter, Security, Depends

from src.auth.dependencies import UserPermissionDependency
from src.auth.permissions import IsAuthenticated
from src.base.dependencies import get_service
from src.payment.models import Payment
from src.payment.schemas import (
    PaymentResponseSchema,
    CreatePaymentRequestSchema
)
from src.payment.services import PaymentService
from src.payment.dependencies import get_available_providers
from src.users import User

payment_router = APIRouter()


@payment_router.get('/providers')
async def get_payment_providers() -> list[str]:
    """Get list of available payment providers.

    Returns:
        List of available payment provider names.
    """
    return get_available_providers()


@payment_router.post('/', response_model=PaymentResponseSchema)
async def create_payment(
        payment_schema: CreatePaymentRequestSchema,
        user: Annotated[
            User, Security(UserPermissionDependency([IsAuthenticated]))
        ],
        service: Annotated[
            PaymentService, Depends(get_service(PaymentService))],
) -> PaymentResponseSchema:
    payment: Payment = await service.create_payment(
        payment_schema,
        user,
    )
    return PaymentResponseSchema.model_validate(payment)

