from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.auth.dependencies import UserPermissionDependency
from src.auth.permissions import IsAuthenticated
from src.base.dependencies import get_service
from src.courses.dependencies import CoursePermissionDependency
from src.courses.models import Course
from src.courses.permissions import IsCourseActive
from src.payment.dependencies import get_available_providers
from src.payment.models import Payment
from src.payment.schemas import (
    CreatePaymentRequestSchema,
    PaymentResponseSchema,
)
from src.payment.services import PaymentService
from src.users import User

payment_router = APIRouter()


@payment_router.get('/providers')
async def get_payment_providers() -> list[str]:
    """Get list of available payment providers.

    Returns:
        List of available payment provider names.

    """
    return get_available_providers()


@payment_router.post('/{course_id}', response_model=PaymentResponseSchema)
async def buy_course(
    payment_schema: CreatePaymentRequestSchema,
    user: Annotated[
        User, Security(UserPermissionDependency([IsAuthenticated]))
    ],
    course: Annotated[
        Course,
        Security(
            CoursePermissionDependency(
                [
                    IsCourseActive,
                ]
            )
        ),
    ],
    service: Annotated[PaymentService, Depends(get_service(PaymentService))],
) -> PaymentResponseSchema:
    payment: Payment = await service.create_payment(
        payment_schema,
        course,
        user,
    )
    return PaymentResponseSchema.model_validate(payment)
