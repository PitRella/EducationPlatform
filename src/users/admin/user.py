from typing import ClassVar

from sqladmin import ModelView

from src.users import User


class UserAdmin(ModelView, model=User):
    """Admin interface for managing a User model in the admin panel."""

    column_list: ClassVar = [
        User.id,
        User.email,
        User.name,
        User.roles,
        User.is_active,
    ]
    form_excluded_columns: ClassVar = [User.password]
    column_searchable_list: ClassVar = [User.email, User.name]
    form_args: ClassVar = {
        'created_at': {'render_kw': {'readonly': True, 'disabled': True}},
        'updated_at': {'render_kw': {'readonly': True, 'disabled': True}},
    }
