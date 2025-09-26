from typing import ClassVar

from sqladmin import ModelView

from src.base.admin import TimestampAdminMixin
from src.payment.models import Payment


class PaymentAdmin(TimestampAdminMixin, ModelView, model=Payment):
    """Admin interface for managing Payment model in the admin panel."""

    column_list: ClassVar = [
        Payment.id,
        Payment.payment_method,
        Payment.amount,
    ]
    form_excluded_columns: ClassVar = [Payment.created_at, Payment.updated_at]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
        'balance': {'render_kw': {'readonly': True, 'disabled': True}},
    }
