from decimal import Decimal
from typing import Any

import stripe

from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentMethodEnum, PaymentStatusEnum
from src.payment.services.providers.base import AbstractProvider
from src.settings import Settings
from src.payment.dto import PaymentResult

settings = Settings.load()

CURRENCY_BASE_MULTIPLIER: int = 100  # Stripe get price in cents


class StripePaymentProviderService(AbstractProvider):
    def __init__(self) -> None:
        stripe.api_key = settings.stripe_settings.SECRET_KEY

    @staticmethod
    def _get_stripe_amount(amount: Decimal) -> int:
        """Stripe get price in cents. So we need to multiply it."""
        return int(amount) * CURRENCY_BASE_MULTIPLIER

    def create_payment(
            self,
            amount: Decimal,
            currency: CurrencyEnum,
            method: PaymentMethodEnum,
            metadata: dict[str, Any] | None = None
    ) -> PaymentResult:
        stripe_result = stripe.PaymentIntent.create(
            amount=self._get_stripe_amount(amount),
            currency=currency,
            payment_method_types=[method],
        )
        return PaymentResult.from_object(stripe_result)

    def payment_status(self, payment_id: str) -> str:
        pass

    def cancel_payment(self, payment_id: str) -> None:
        pass

    def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        pass
