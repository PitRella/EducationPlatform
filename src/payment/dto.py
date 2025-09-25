from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from src.base.dto import BaseDTO
from src.courses.enums import CurrencyEnum
from src.payment.enums import PaymentStatusEnum


@dataclass
class PaymentResult(BaseDTO):
    """Represents the result of a payment processing operation.

    This class encapsulates the essential information about a transaction,
    including its status, amount, and any associated messages or URLs.

    Attributes:
        id (str): The unique identifier for the payment transaction.
        status (PaymentStatusEnum): The current status of the payment
            (e.g., completed, pending, failed).
        amount (Decimal): The monetary amount of the payment.
        currency (CurrencyEnum): The currency code for the payment amount.
        redirect_url (str | None): URL where the user should be redirected
            after payment processing, if applicable. Defaults to None.
        error_message (str | None): Description of any error that occurred
            during payment processing. Defaults to None.

    """

    id: str
    status: PaymentStatusEnum
    amount: Decimal
    currency: CurrencyEnum
    redirect_url: str | None = None
    error_message: str | None = None


# Stripe Models
@dataclass
class StripeWebhookRequest(BaseDTO):
    """Represents request information in a Stripe webhook notification.

    This class encapsulates the request-specific information received in Stripe
    webhook events, including identifiers used for tracking and idempotency.

    Attributes:
        id (str): The unique identifier for the request.
        idempotency_key (str | None): The idempotency key used to prevent
            duplicate processing. Defaults to None.

    """

    id: str
    idempotency_key: str | None = None


@dataclass
class StripeWebhookShippingAddress(BaseDTO):
    """Represents a shipping address in a Stripe webhook notification.

    This class encapsulates the shipping address details received in webhook
    events, providing a structured representation of the delivery location.

    Attributes:
        city (str | None): The city name for the shipping address.
        country (str | None): The country code for the shipping address.
        line1 (str | None): The first line of the street address.
        line2 (str | None): The second line of the street address (optional).
            Defaults to None.
        postal_code (str | None): The postal or ZIP code. Defaults to None.
        state (str | None): The state, county, or region. Defaults to None.

    """

    city: str | None = None
    country: str | None = None
    line1: str | None = None
    line2: str | None = None
    postal_code: str | None = None
    state: str | None = None


@dataclass
class StripeWebhookShipping(BaseDTO):
    """Represents shipping information in a Stripe webhook notification.

    This class encapsulates shipping-related information received in webhook
    events, including delivery address, recipient details, information.

    Attributes:
        address (StripeWebhookShippingAddress): The shipping address details.
        name (str): The recipient's name for shipping.
        carrier (str | None): The shipping carrier service provider.
        phone (str | None): Contact phone number for shipping.
        tracking_number (str | None): Shipping tracking number if available.
            Defaults to None.

    """

    address: StripeWebhookShippingAddress
    name: str
    carrier: str | None = None
    phone: str | None = None
    tracking_number: str | None = None


@dataclass
class StripeWebhookPaymentMethodOptionsCard(BaseDTO):
    """Represents card-specific payment method options in a Stripe webhook.

    This class encapsulates the configuration options specific to card payments
    received in Stripe webhook events, including 3D Secure settings and other
    card-related options.

    Attributes:
        request_three_d_secure (str): The 3D Secure authentication setting
            for the payment ("automatic" or "any").
        installments (Any | None): Configuration for installment payments,
            if applicable. Defaults to None.
        mandate_options (Any | None): Options for mandate creation when
            setting up future payments. Defaults to None.
        network (str | None): The card network to process this payment.
            Defaults to None.

    """

    request_three_d_secure: str
    installments: Any | None = None
    mandate_options: Any | None = None
    network: str | None = None


@dataclass
class StripeWebhookPaymentMethodOptions(BaseDTO):
    """Represents payment method options in a Stripe webhook notification.

    This class encapsulates the payment-method-specific options received in
    Stripe webhook events, particularly focusing on card payment config.

    Attributes:
        card (StripeWebhookPaymentMethodOptionsCard): Configuration options
            specific to card payments, including 3D Secure settings.

    """

    card: StripeWebhookPaymentMethodOptionsCard


@dataclass
class StripeWebhookAmountDetails(BaseDTO):
    """Represents the detailed breakdown of payment amounts in a Stripe.

    This class encapsulates the detailed amount information received
    events, specifically for tips and other potential amount-related details.

    Attributes:
        tip (dict[str, Any]): Dictionary containing tip-related information,
            such as amount and currency.

    """

    tip: dict[str, Any]


@dataclass
class StripeWebhookPaymentIntent(BaseDTO):
    """Represents a Stripe Payment Intent object received in webhook.

    This class encapsulates the complete structure of a Payment Intent
    from Stripe's webhook events. It contains detailed information about,
    including amount, status, and various configuration options.

    Attributes:
        id (str): Unique identifier for the payment intent.
        object (str): String representing the object type.
        amount (int): Amount intended to be collected.
        amount_capturable (int): Amount available to capture.
        amount_details (StripeWebhookAmountDetails): Breakdown of amounts.
        amount_received (int): Amount received (in smallest currency unit).
        capture_method (str): Method of capture ("automatic" or "manual").
        client_secret (str): Client secret used to initialize payment.
        confirmation_method (str): Method of confirmation.
        created (int): Timestamp of when the intent was created.
        currency (str): Three-letter ISO currency code.
        description (str | None): Description of the payment intent.
        livemode (bool): Whether this intent was created in live mode.
        metadata (dict[str, Any]): Set of key-value pairs attached.
        payment_method (str): ID of the payment method used.
        payment_method_options (StripeWebhookPaymentMethodOptions): Config.
        payment_method_types (list[str]): Types of payment methods.
        status (str): Status of the intent.
        application (str | None): ID of the Connect application.
        application_fee_amount (int | None): Fee amount for the application.
        automatic_payment_methods (Any | None): Settings for automatic payment.
        canceled_at (int | None): Timestamp of cancellation if canceled.
        cancellation_reason (str | None): Reason for cancellation if canceled.
        customer (str | None): ID of the customer this intent belongs to.
        excluded_payment_method_types (Any | None): Payment methods to exclude.
        last_payment_error (Any | None): Error information from payment.
        latest_charge (str | None): ID of the latest charge.
        next_action (Any | None): Next action required to process payment.
        on_behalf_of (str | None): Account ID payment is collected
        payment_method_configuration_details (Any | None): Payment method.
        processing (Any | None): Processing information.
        receipt_email (str | None): Email address for receipt.
        review (Any | None): ID of the review associated with intent.
        setup_future_usage (Any | None): Setup future usage settings.
        shipping (StripeWebhookShipping | None): Shipping information.
        source (str | None): Payment source ID.
        statement_descriptor (str | None): Statement descriptor.
        statement_descriptor_suffix (str | None): Statement descriptor suffix.
        transfer_data (Any | None): Transfer data for the intent.
        transfer_group (str | None): Transfer group identifier.

    """

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
    """Represents the data field within a Stripe webhook event notification.

    This class encapsulates the actual payment intent data sent by Stripe
    in webhook notifications. It contains detailed information about the
    payment transaction and its current state.

    Attributes:
        object (StripeWebhookPaymentIntent): The payment intent object
            containing detailed information about the payment transaction.

    """

    object: StripeWebhookPaymentIntent


@dataclass
class StripeWebhookPayload(BaseDTO):
    """Represents a Stripe webhook payload received from events.

    This class encapsulates the data structure of webhook notifications sent by
    Stripe when payment-related events occur.

    Attributes:
        id (str): Unique identifier of the webhook event.
        object (str): Type of object, typically "event".
        api_version (str): Version of the Stripe API used.
        created (int): Timestamp of when the event was created.
        data (StripeWebhookData): The event data containing payment details.
        livemode (bool): Whether this event was generated.
        pending_webhooks (int): Number of webhook deliveries still pending.
        request (StripeWebhookRequest): Information about the request.
        type (str): Type of event (e.g., "payment_intent.succeeded").

    """

    id: str
    object: str
    api_version: str
    created: int
    data: StripeWebhookData
    livemode: bool
    pending_webhooks: int
    request: StripeWebhookRequest
    type: str
