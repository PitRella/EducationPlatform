import uuid

from pydantic import BaseModel
from src.base.schemas import BaseSchema


class CreatePaymentRequestSchema(BaseModel):
    course_id: uuid.UUID


class PaymentResponseSchema(BaseSchema):
    id: uuid.UUID
    course_id: uuid.UUID
    user_id: uuid.UUID
