from decimal import Decimal
from typing import Any

import stripe

from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentMethodEnum, PaymentStatusEnum
from src.payment.services.providers.base import AbstractProvider
from src.settings import Settings
from src.payment.dto import PaymentResult

settings = Settings.load()


class StripePaymentProviderService(AbstractProvider):
    def __init__(self) -> None:
        stripe.api_key = settings.stripe_settings.SECRET_KEY

    def create_payment(
            self,
            amount: Decimal,
            currency: CurrencyEnum,
            method: PaymentMethodEnum,
            metadata: dict[str, Any] | None = None
    ) -> PaymentResult:
        stripe_result = stripe.PaymentIntent.create(
            amount=int(amount),
            currency=currency,
            payment_method_types=[method],
        )
        return PaymentResult.from_object(stripe_result)

    def payment_status(self, payment_id: str) -> str:
        pass

    def payment_cancel(self, payment_id: str) -> None:
        pass

    def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        pass
