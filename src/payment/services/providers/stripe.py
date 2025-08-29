from decimal import Decimal

import stripe

from src.settings import Settings

settings = Settings.load()


class StripePaymentService:
    def __init__(self) -> None:
        stripe.api_key = settings.stripe_settings.SECRET_KEY

    def create_payment(self, price: Decimal) -> stripe.PaymentIntent:
        return stripe.PaymentIntent.create(
            amount=int(price),
            currency='usd',
            payment_method_types=['card'],
        )