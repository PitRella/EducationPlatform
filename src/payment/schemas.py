import uuid

from pydantic import BaseModel

from src.base.schemas import BaseSchema
from src.payment.enums import PaymentMethodEnum, PaymentProviderEnum


class CreatePaymentRequestSchema(BaseModel):
    """Schema representing a payment request.

    Contains information required to initiate a payment transaction,
    including the payment method and provider to be used.

    Attributes:
        payment_method (PaymentMethodEnum): The method of payment .
        provider (PaymentProviderEnum): The payment service provider.

    """

    payment_method: PaymentMethodEnum
    provider: PaymentProviderEnum


class PaymentResponseSchema(BaseSchema):
    """Schema representing a payment response.

    Contains information about a processed payment, including unique id
    for the payment itself, associated course, and user who made the payment.

    Attributes:
        id (uuid.UUID): Unique identifier of the payment.
        course_id (uuid.UUID): Identifier of the course being purchased.
        user_id (uuid.UUID): Identifier of the user making the payment.

    """

    id: uuid.UUID
    course_id: uuid.UUID
    user_id: uuid.UUID
