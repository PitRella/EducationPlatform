from enum import StrEnum


class PaymentStatusEnum(StrEnum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class PaymentMethodEnum(StrEnum):
    """Payment method enumeration."""

    CARD = "card"
    PAYPAL = "paypal"
    CRYPTO = "crypto"
    BANK_TRANSFER = "bank_transfer"


class PaymentProviderEnum(StrEnum):
    """Payment provider enumeration."""

    STRIPE = "stripe"
    PAYPAL = "paypal"
    LIQPAY = "liqpay"
    WAYFORPAY = "wayforpay"
