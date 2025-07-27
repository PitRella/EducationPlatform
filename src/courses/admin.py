from typing import ClassVar

from sqladmin import ModelView

from src.courses.models import Course


class CourseAdmin(ModelView, model=Course):
    """Admin interface for managing Course model in the admin panel."""

    column_list: ClassVar = [
        Course.title,
        Course.is_active,
        Course.rating,
        Course.price,
        Course.language,
    ]

    form_args: ClassVar = {
        'created_at': {'render_kw': {'readonly': True, 'disabled': True}},
        'updated_at': {'render_kw': {'readonly': True, 'disabled': True}},
        'slug': {'render_kw': {'readonly': True, 'disabled': True}},
    }
