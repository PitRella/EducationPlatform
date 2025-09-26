from typing import ClassVar

from sqladmin import ModelView

from src.base.admin import TimestampAdminMixin
from src.courses.models import Course


class CourseAdmin(TimestampAdminMixin, ModelView, model=Course):
    """Admin interface for managing a Course model in the admin panel."""

    column_list: ClassVar = [
        Course.title,
        Course.is_active,
        Course.rating,
        Course.price,
        Course.language,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
        'slug': {'render_kw': {'readonly': True, 'disabled': True}},
    }
