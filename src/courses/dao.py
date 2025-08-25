from sqlalchemy.orm import selectinload

from src.base.dao import BaseDAO, Model
from src.courses.models import Course
from src.courses.schemas import BaseCreateCourseRequestSchema
from typing import Any

from sqlalchemy import (
    Result,
    Select,
    select,
)


class CourseDAO(BaseDAO[Course, BaseCreateCourseRequestSchema]):
    async def get_course_with_lessons(
            self,
            *filters: Any,
            **filters_by: Any
    ) -> Course | None:
        return await self.get_one_with_relations(
            *filters,
            relations=["lessons"],
            **filters_by
        )
