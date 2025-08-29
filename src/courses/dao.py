from typing import Any

from src.base.dao import BaseDAO
from src.courses.models import Course
from src.courses.schemas import BaseCreateCourseRequestSchema


class CourseDAO(BaseDAO[Course, BaseCreateCourseRequestSchema]):
    """Data access object (DAO) for courses.

    Extends BaseDAO to provide functionality specific to the Course model,
    including querying courses with their related lessons.
    """

    async def get_published_course(
            self,
            *filters: Any,
            **filters_by: Any
    ) -> Course | None:
        return await self.get_one(
            *filters,
            is_active=True,
            **filters_by
        )

    async def get_course_with_lessons(
            self, *filters: Any, **filters_by: Any
    ) -> Course | None:
        """Retrieve a course with its related lessons.

        This method fetches a single course matching the given filters and
        eagerly loads its associated lessons relation.

        Args:
            *filters (Any): Positional filters applied to the query.
            **filters_by (Any): Keyword-based filters applied to the query.

        Returns:
            Course | None: The course with its lessons loaded, or None if no
            course matches the filters.

        """
        return await self.get_one_with_relations(
            *filters, relations=['lessons'], **filters_by
        )
