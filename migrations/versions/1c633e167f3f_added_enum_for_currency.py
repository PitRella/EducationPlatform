"""added_enum_for_currency

Revision ID: 1c633e167f3f
Revises: f504084a606c
Create Date: 2025-08-29 21:20:14.293005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c633e167f3f'
down_revision: Union[str, None] = 'f504084a606c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema: convert currency from VARCHAR(3) to ENUM."""
    # сначала создаём сам enum (если он ещё не создан)
    currency_enum = sa.Enum("USD", "EUR", "UAH", name="currencyenum")
    currency_enum.create(op.get_bind(), checkfirst=True)

    # потом меняем тип колонки с кастом
    op.alter_column(
        "payments",
        "currency",
        existing_type=sa.VARCHAR(length=3),
        type_=currency_enum,
        existing_comment="Payment currency (ISO 4217)",
        existing_nullable=False,
        postgresql_using="currency::text::currencyenum",
    )


def downgrade() -> None:
    """Downgrade schema: convert currency from ENUM back to VARCHAR(3)."""
    op.alter_column(
        "payments",
        "currency",
        existing_type=sa.Enum("USD", "EUR", "UAH", name="currencyenum"),
        type_=sa.VARCHAR(length=3),
        existing_comment="Payment currency (ISO 4217)",
        existing_nullable=False,
        postgresql_using="currency::text",
    )

    sa.Enum("USD", "EUR", "UAH", name="currencyenum").drop(op.get_bind(), checkfirst=True)
