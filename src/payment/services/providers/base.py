from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Any

from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentMethodEnum, PaymentStatusEnum


class AbstractProvider(ABC):
    @abstractmethod
    def create_payment(
            self,
            amount: Decimal,
            currency: CurrencyEnum,
            method: PaymentMethodEnum,
            metadata: Optional[dict[str, Any]] = None
    ) -> None:
        pass

    @abstractmethod
    def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        pass

    @abstractmethod
    def cancel_payment(self, payment_id: str) -> None:
        pass
