from abc import ABC, abstractmethod
from decimal import Decimal

from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentMethodEnum


class AbstractProvider(ABC):
    @abstractmethod
    def create_payment(
            self,
            amount: Decimal,
            currency: CurrencyEnum,
            method: PaymentMethodEnum
    ) -> None:
        pass
