from dataclasses import dataclass
from decimal import Decimal

from src.base.dto import BaseDTO
from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentStatusEnum
from typing import Any, Optional

@dataclass
class PaymentResult(BaseDTO):
    status: PaymentStatusEnum
    amount: Decimal
    currency: CurrencyEnum
    redirect_url: str | None = None
    error_message: str | None = None

# Stripe

@dataclass
class StripeWebhookRequest:
    id: str
    idempotency_key: Optional[str]

@dataclass
class StripeWebhookShippingAddress:
    city: Optional[str]
    country: Optional[str]
    line1: Optional[str]
    line2: Optional[str]
    postal_code: Optional[str]
    state: Optional[str]

@dataclass
class StripeWebhookShipping:
    address: StripeWebhookShippingAddress
    carrier: Optional[str]
    name: str
    phone: Optional[str]
    tracking_number: Optional[str]

@dataclass
class StripeWebhookPaymentMethodOptionsCard:
    installments: Optional[Any]
    mandate_options: Optional[Any]
    network: Optional[str]
    request_three_d_secure: str

@dataclass
class StripeWebhookPaymentIntent:
    id: str
    object: str
    amount: int
    amount_capturable: int
    amount_details: dict[str, Any]
    amount_received: int
    application: Optional[str]
    application_fee_amount: Optional[int]
    automatic_payment_methods: Optional[Any]
    canceled_at: Optional[int]
    cancellation_reason: Optional[str]
    capture_method: str
    client_secret: str
    confirmation_method: str
    created: int
    currency: str
    customer: Optional[str]
    description: Optional[str]
    excluded_payment_method_types: Optional[Any]
    last_payment_error: Optional[Any]
    latest_charge: Optional[str]
    livemode: bool
    metadata: dict[str, Any]
    next_action: Optional[Any]
    on_behalf_of: Optional[str]
    payment_method: str
    payment_method_configuration_details: Optional[Any]
    payment_method_options: dict[str, StripeWebhookPaymentMethodOptionsCard]
    payment_method_types: list[str]
    processing: Optional[Any]
    receipt_email: Optional[str]
    review: Optional[Any]
    setup_future_usage: Optional[Any]
    shipping: Optional[StripeWebhookShipping]
    source: Optional[str]
    statement_descriptor: Optional[str]
    statement_descriptor_suffix: Optional[str]
    status: str
    transfer_data: Optional[Any]
    transfer_group: Optional[str]

@dataclass
class StripeWebhookData:
    object: StripeWebhookPaymentIntent

@dataclass
class StripeWebhookPayload(BaseDTO):
    id: str
    object: str
    api_version: str
    created: int
    data: StripeWebhookData
    livemode: bool
    pending_webhooks: int
    request: StripeWebhookRequest
    type: str
