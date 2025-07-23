from typing import ClassVar

from sqladmin import ModelView

from src.users import Author


class AuthorAdmin(ModelView, model=Author):
    """Admin interface for managing Author model in the admin panel."""

    column_list: ClassVar = [
        Author.id,
        Author.user,
        Author.is_verified,
        Author.balance,
    ]

    form_args: ClassVar = {
        'slug': {'render_kw': {'readonly': True, 'disabled': True}},
        'balance': {'render_kw': {'readonly': True, 'disabled': True}},
        'created_at': {'render_kw': {'readonly': True, 'disabled': True}},
        'updated_at': {'render_kw': {'readonly': True, 'disabled': True}},
    }
