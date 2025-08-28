from src.base.dao import BaseDAO
from src.lessons.models import Lesson
from typing import Any

from src.lessons.schemas import CreateLessonRequestSchema


class LessonDAO(BaseDAO[Lesson, CreateLessonRequestSchema]):
    """Data access object (DAO) for lessons.

    Extends the BaseDAO with functionality specific to the Lesson model.
    Provides methods to query lessons with their related entities.
    """

    async def get_lesson_with_course(
            self,
            *filters: Any,
            **filters_by: Any
    ) -> Lesson | None:
        """Retrieve a lesson with its related course.

        This method fetches a single lesson that matches the given filters
        and eagerly loads its associated course relation.

        Args:
            *filters (Any): Positional filters applied to the query.
            **filters_by (Any): Keyword-based filters applied to the query.

        Returns:
            Lesson | None: The lesson instance with its course loaded, or
            None if no lesson matches the filters.
        """
        return await self.get_one_with_relations(
            *filters,
            relations=["course"],
            **filters_by
        )
