from src.base.dao import BaseDAO
from src.lessons.models import Lesson
from typing import Any

from src.lessons.schemas import CreateLessonRequestSchema


class LessonDAO(BaseDAO[Lesson, CreateLessonRequestSchema]):
    async def get_lesson_with_course(
            self,
            *filters: Any,
            **filters_by: Any
    ) -> Lesson | None:
        return await self.get_one_with_relations(
            *filters,
            relations=["course"],
            **filters_by
        )
