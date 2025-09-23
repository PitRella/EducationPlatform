from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from src.base.dto import BaseDTO
from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentStatusEnum


@dataclass
class PaymentResult(BaseDTO):
    id: str
    status: PaymentStatusEnum
    amount: Decimal
    currency: CurrencyEnum
    redirect_url: str | None = None
    error_message: str | None = None


# Stripe Models
@dataclass
class StripeWebhookRequest(BaseDTO):
    id: str
    idempotency_key: str | None = None


@dataclass
class StripeWebhookShippingAddress(BaseDTO):
    city: str | None = None
    country: str | None = None
    line1: str | None = None
    line2: str | None = None
    postal_code: str | None = None
    state: str | None = None


@dataclass
class StripeWebhookShipping(BaseDTO):
    address: StripeWebhookShippingAddress
    name: str
    carrier: str | None = None
    phone: str | None = None
    tracking_number: str | None = None


@dataclass
class StripeWebhookPaymentMethodOptionsCard(BaseDTO):
    request_three_d_secure: str
    installments: Any | None = None
    mandate_options: Any | None = None
    network: str | None = None


@dataclass
class StripeWebhookPaymentMethodOptions(BaseDTO):
    card: StripeWebhookPaymentMethodOptionsCard


@dataclass
class StripeWebhookAmountDetails(BaseDTO):
    tip: dict[str, Any]


@dataclass
class StripeWebhookPaymentIntent(BaseDTO):
    id: str
    object: str
    amount: int
    amount_capturable: int
    amount_details: StripeWebhookAmountDetails
    amount_received: int
    capture_method: str
    client_secret: str
    confirmation_method: str
    created: int
    currency: str
    description: str | None
    livemode: bool
    metadata: dict[str, Any]
    payment_method: str
    payment_method_options: StripeWebhookPaymentMethodOptions
    payment_method_types: list[str]
    status: str

    # Optional fields
    application: str | None = None
    application_fee_amount: int | None = None
    automatic_payment_methods: Any | None = None
    canceled_at: int | None = None
    cancellation_reason: str | None = None
    customer: str | None = None
    excluded_payment_method_types: Any | None = None
    last_payment_error: Any | None = None
    latest_charge: str | None = None
    next_action: Any | None = None
    on_behalf_of: str | None = None
    payment_method_configuration_details: Any | None = None
    processing: Any | None = None
    receipt_email: str | None = None
    review: Any | None = None
    setup_future_usage: Any | None = None
    shipping: StripeWebhookShipping | None = None
    source: str | None = None
    statement_descriptor: str | None = None
    statement_descriptor_suffix: str | None = None
    transfer_data: Any | None = None
    transfer_group: str | None = None


@dataclass
class StripeWebhookData(BaseDTO):
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
