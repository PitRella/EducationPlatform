from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from src.courses.enums import CurrencyEnum
from src.payment.dto import PaymentResult
from src.payment.enums import PaymentMethodEnum, PaymentStatusEnum


class AbstractProvider(ABC):
    """Abstract base class for payment provider implementations.

    Defines the interface that all payment providers must implement to handle
    payment operations like creating payments, checking status, canceling and
    refunding payments.
    """

    @abstractmethod
    def create_payment(
        self,
        amount: Decimal,
        currency: CurrencyEnum,
        method: PaymentMethodEnum,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentResult:
        """Create a new payment transaction.

        Args:
            amount: The payment amount.
            currency: The currency for the payment.
            method: The payment method to be used.
            metadata: Additional payment metadata.

        Returns:
            PaymentResult containing the payment details and status.

        """

    @abstractmethod
    def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        """Get the current status of a payment.

        Args:
            payment_id: The unique identifier of the payment.

        Returns:
            Current status of the payment.

        """

    @abstractmethod
    def cancel_payment(self, payment_id: str) -> None:
        """Cancel an existing payment.

        Args:
            payment_id: The unique identifier of the payment to cancel.

        """

    @abstractmethod
    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal,
    ) -> None:
        """Refund an existing payment, either fully or partially.

        Args:
            payment_id: The unique identifier of the payment to refund.
            amount: Optional amount to refund. If None, refunds the full amount.

        """
