from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from src.base.dto import BaseDTO
from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentStatusEnum


@dataclass
class PaymentResult(BaseDTO):
    payment_id: str
    status: PaymentStatusEnum
    amount: Decimal
    currency: CurrencyEnum
    provider_data: dict[str, Any]
    redirect_url: str | None = None
    error_message: str | None = None
