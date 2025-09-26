from typing import ClassVar

from sqladmin import ModelView

from src.base.admin import TimestampAdminMixin
from src.lessons.models import Lesson


class LessonAdmin(TimestampAdminMixin, ModelView, model=Lesson):
    """Admin interface for managing a Lesson model in the admin panel."""
    column_list: ClassVar = [
        Lesson.title,
        Lesson.slug,
        Lesson.is_free,
        Lesson.is_published,
    ]
    form_excluded_columns: ClassVar = [Lesson.created_at, Lesson.updated_at]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }
