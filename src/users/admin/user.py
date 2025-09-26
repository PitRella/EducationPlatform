from typing import ClassVar

from sqladmin import ModelView

from src.base.admin import TimestampAdminMixin
from src.users import User


class UserAdmin(TimestampAdminMixin, ModelView, model=User):
    """Admin interface for managing a User model in the admin panel."""

    column_list: ClassVar = [
        User.id,
        User.email,
        User.name,
        User.role,
        User.is_active,
    ]
    form_excluded_columns: ClassVar = [User.created_at,  User.updated_at, User.purchased_courses, User.payments ]
    column_searchable_list: ClassVar = [User.email, User.name]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }
