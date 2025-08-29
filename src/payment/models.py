import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Any

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import BaseTimeStampMixin, BaseUUIDMixin
from src.courses.enums import CurrencyEnum
from src.payment.enums import (
    PaymentStatusEnum,
    PaymentMethodEnum,
    PaymentProviderEnum
)

if TYPE_CHECKING:
    from src.courses.models import Course
    from src.users.models import User


class Payment(BaseUUIDMixin, BaseTimeStampMixin):
    """Payment model for course purchases.

    Attributes:
        id: Primary key (UUID).
        user_id: User who made the payment.
        course_id: Course being purchased.
        amount: Payment amount.
        currency: Payment currency.
        status: Payment status.
        payment_method: Method used for payment.
        provider: Payment provider.
        provider_payment_id: External payment ID from provider.
        provider_payment_intent_id: Payment intent ID (for Stripe).
        metadata: Additional payment data as JSON.
        failure_reason: Reason for payment failure.
        refund_amount: Amount refunded (if any).
        refunded_at: Refund timestamp.
        processed_at: Payment processing completion timestamp.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = 'payments'

    # Relationships
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='User who made the payment'
    )
    user: Mapped['User'] = relationship(back_populates='payments')

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('courses.id', ondelete='CASCADE'),
        nullable=False,
        comment='Course being purchased'
    )

    # Payment details
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment='Payment amount'
    )
    currency: Mapped[CurrencyEnum] = mapped_column(
        Enum(CurrencyEnum),
        nullable=False,
        comment='Payment currency (ISO 4217)'
    )

    # Status and method
    status: Mapped[PaymentStatusEnum] = mapped_column(
        Enum(PaymentStatusEnum),
        nullable=False,
        default=PaymentStatusEnum.PENDING,
        index=True,
        comment='Payment status'
    )
    payment_method: Mapped[PaymentMethodEnum] = mapped_column(
        Enum(PaymentMethodEnum),
        nullable=False,
        comment='Payment method used'
    )

    # Provider information
    provider: Mapped[PaymentProviderEnum] = mapped_column(
        Enum(PaymentProviderEnum),
        nullable=False,
        comment='Payment provider'
    )
    provider_payment_id: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment='External payment ID from provider'
    )
    provider_payment_intent_id: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment='Payment intent ID (Stripe)'
    )

    # Additional data
    additional_data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=True,
        comment='Additional payment metadata as JSON'
    )
    failure_reason: Mapped[str] = mapped_column(
        String(512),
        nullable=True,
        comment='Reason for payment failure'
    )

    # Refund information
    refund_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment='Amount refunded'
    )
    refunded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment='Refund timestamp'
    )

    # Processing timestamp
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment='Payment processing completion timestamp'
    )
