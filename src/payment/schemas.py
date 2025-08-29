import uuid

from pydantic import BaseModel
from src.base.schemas import BaseSchema
from src.payment.enums import PaymentMethodEnum, PaymentProviderEnum


class CreatePaymentRequestSchema(BaseModel):
    course_id: uuid.UUID
    payment_method: PaymentMethodEnum
    provider: PaymentProviderEnum


class PaymentResponseSchema(BaseSchema):
    id: uuid.UUID
    course_id: uuid.UUID
    user_id: uuid.UUID
