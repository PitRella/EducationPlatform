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
    async def get_course_with_lessons(self, *filters: Any, **filters_by: Any) -> Course | None:
        query: Select[Any] = (
            select(self.model).where(*filters).filter_by(**filters_by).options(
                selectinload(self.model.lessons))
        )
        result: Result[Any] = await self.session.execute(query)
        return result.scalar_one_or_none()
