from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, Dict, List

from src.base.dto import BaseDTO
from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentStatusEnum


@dataclass
class PaymentResult(BaseDTO):
    status: PaymentStatusEnum
    amount: Decimal
    currency: CurrencyEnum
    redirect_url: Optional[str] = None
    error_message: Optional[str] = None


# Stripe Models
@dataclass
class StripeWebhookRequest(BaseDTO):
    id: str
    idempotency_key: Optional[str] = None


@dataclass
class StripeWebhookShippingAddress(BaseDTO):
    city: Optional[str] = None
    country: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None


@dataclass
class StripeWebhookShipping(BaseDTO):
    address: StripeWebhookShippingAddress
    name: str
    carrier: Optional[str] = None
    phone: Optional[str] = None
    tracking_number: Optional[str] = None


@dataclass
class StripeWebhookPaymentMethodOptionsCard(BaseDTO):
    request_three_d_secure: str
    installments: Optional[Any] = None
    mandate_options: Optional[Any] = None
    network: Optional[str] = None


@dataclass
class StripeWebhookPaymentMethodOptions(BaseDTO):
    card: StripeWebhookPaymentMethodOptionsCard


@dataclass
class StripeWebhookAmountDetails(BaseDTO):
    tip: Dict[str, Any]


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
    description: Optional[str]
    livemode: bool
    metadata: Dict[str, Any]
    payment_method: str
    payment_method_options: StripeWebhookPaymentMethodOptions
    payment_method_types: List[str]
    status: str

    # Optional fields
    application: Optional[str] = None
    application_fee_amount: Optional[int] = None
    automatic_payment_methods: Optional[Any] = None
    canceled_at: Optional[int] = None
    cancellation_reason: Optional[str] = None
    customer: Optional[str] = None
    excluded_payment_method_types: Optional[Any] = None
    last_payment_error: Optional[Any] = None
    latest_charge: Optional[str] = None
    next_action: Optional[Any] = None
    on_behalf_of: Optional[str] = None
    payment_method_configuration_details: Optional[Any] = None
    processing: Optional[Any] = None
    receipt_email: Optional[str] = None
    review: Optional[Any] = None
    setup_future_usage: Optional[Any] = None
    shipping: Optional[StripeWebhookShipping] = None
    source: Optional[str] = None
    statement_descriptor: Optional[str] = None
    statement_descriptor_suffix: Optional[str] = None
    transfer_data: Optional[Any] = None
    transfer_group: Optional[str] = None


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
