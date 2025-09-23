from decimal import Decimal
from typing import Any

import stripe

from src.courses.enums import CurrencyEnum
from src.payment.dto import PaymentResult
from src.payment.enums import PaymentMethodEnum, PaymentStatusEnum
from src.payment.services.providers.base import AbstractProvider
from src.settings import Settings

settings = Settings.load()

CURRENCY_BASE_MULTIPLIER: int = 100  # Stripe get price in cents


class StripePaymentProviderService(AbstractProvider):
    """Stripe payment provider service implementation.

    Handles payment processing with the Stripe API including create payments,
    checking payment status, and canceling payments. Uses stripe-python SDK
    for API communication.

    Attributes:
        api_key (str): Stripe API secret key loaded from settings.

    """

    def __init__(self) -> None:
        """Initialize the Stripe payment provider service.

        Sets up the Stripe API key from app settings during installation.
        The API key is required for all Stripe API operations.
        """
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
        metadata: dict[str, Any] | None = None,
    ) -> PaymentResult:
        """Create new payment intent through Stripe API.

        Creates a PaymentIntent object in Stripe with the specified amount,
        currency and payment method. The PaymentIntent represents the intent
        to collect payment from a customer.

        Args:
            amount (Decimal): Payment amount to charge.
            currency (CurrencyEnum): Currency code for the payment.
            method (PaymentMethodEnum): Payment method to use.
            metadata (dict[str, Any] | None, optional): Additional metadata
                for the payment. Defaults to None.

        Returns:
            PaymentResult: Object containing payment details and status.

        """
        stripe_result = stripe.PaymentIntent.create(
            amount=self._get_stripe_amount(amount),
            currency=currency,
            payment_method_types=[method],
        )
        return PaymentResult.from_object(stripe_result)

    def payment_status(self, payment_id: str) -> str:
        """Get raw payment status from Stripe.

        Args:
            payment_id (str): The Stripe payment intent ID.

        Returns:
            str: Raw payment status string from Stripe.

        """
        payment = stripe.PaymentIntent.retrieve(payment_id)
        return payment.status

    def cancel_payment(self, payment_id: str) -> None:
        """Cancel a payment intent in Stripe.

        Args:
            payment_id (str): The Stripe payment intent ID to cancel.

        """
        stripe.PaymentIntent.cancel(payment_id)

    def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        """Get normalized payment status.

        Args:
            payment_id (str): The Stripe payment intent ID.

        Returns:
            PaymentStatusEnum: Normalized payment status enum.

        """
        status = self.payment_status(payment_id)
        if status in ['succeeded', 'processing']:
            return PaymentStatusEnum.COMPLETED
        if status == 'requires_payment_method':
            return PaymentStatusEnum.PENDING
        return PaymentStatusEnum.FAILED
