from sqlalchemy.orm import selectinload

from src.base.dao import BaseDAO, Model
from src.lessons.models import Lesson
from typing import Any

from sqlalchemy import (
    Result,
    Select,
    select,
)

from src.lessons.schemas import CreateLessonRequestSchema


class LessonDAO(BaseDAO[Lesson, CreateLessonRequestSchema]):
    async def get_lesson_with_course(
            self,
            *filters: Any,
            **filters_by: Any
    ) -> Lesson | None:
        query: Select[Any] = (
            select(self.model).where(*filters).filter_by(**filters_by).options(
                selectinload(self.model.course))
        )
        result: Result[Any] = await self.session.execute(query)
        return result.scalar_one_or_none()
