from decimal import Decimal

import stripe

from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentMethodEnum
from src.payment.services.providers.base import AbstractProvider
from src.settings import Settings

settings = Settings.load()


class StripePaymentProviderService(AbstractProvider):
    def __init__(self) -> None:
        stripe.api_key = settings.stripe_settings.SECRET_KEY

    def create_payment(
            self,
            amount: Decimal,
            currency: CurrencyEnum,
            method: PaymentMethodEnum
    ) -> None:
        stripe.PaymentIntent.create(
            amount=int(amount),
            currency=currency,
            payment_method_types=[method],
        )