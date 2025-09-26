from typing import ClassVar

from sqladmin import ModelView

from src.base.admin import TimestampAdminMixin
from src.users import Author


class AuthorAdmin(TimestampAdminMixin, ModelView, model=Author):
    """Admin interface for managing Author model in the admin panel."""

    column_list: ClassVar = [
        Author.id,
        Author.user,
        Author.is_verified,
        Author.balance,
    ]
    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
        'slug': {'render_kw': {'readonly': True, 'disabled': True}},
        'balance': {'render_kw': {'readonly': True, 'disabled': True}},
    }
