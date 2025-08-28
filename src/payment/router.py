from typing import Annotated

from fastapi import APIRouter, Security

from src.auth.dependencies import UserPermissionDependency
from src.auth.permissions import IsAuthenticated
from src.payment.schemas import (
    PaymentResponseSchema,
    CreatePaymentRequestSchema
)
from src.users import User

payment_router = APIRouter()


@payment_router.post('/', response_model=PaymentResponseSchema)
async def create_payment(
        payment_schema: CreatePaymentRequestSchema,
        user: Annotated[
            User, Security(UserPermissionDependency([IsAuthenticated]))
        ],
) -> PaymentResponseSchema:
    pass
