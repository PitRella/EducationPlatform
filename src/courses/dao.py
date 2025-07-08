import uuid
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import Result, Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.courses.models import Course
from src.courses.schemas import (
    BaseCreateCourseSchema,
)


class AbstractCourseDAO(ABC):
    """Abstract class for Course Data Access Objects."""

    def __init__(self, db_session: AsyncSession):
        """Initialize a new CourseDAO instance."""
        self._db_session: AsyncSession = db_session

    @property
    def session(self) -> AsyncSession:
        """Return the current SQLAlchemy session."""
        return self._db_session

    @abstractmethod
    async def create_course(
        self, course_schema: BaseCreateCourseSchema
    ) -> Course:
        """Create a new course in the database."""
        raise NotImplementedError

    @abstractmethod
    async def get_course(self, course_id: uuid.UUID) -> Course | None:
        """Get a course by its ID."""
        raise NotImplementedError


class CourseDAO(AbstractCourseDAO):
    """Course Data Access Object."""

    async def create_course(
        self, course_schema: BaseCreateCourseSchema
    ) -> Course:
        """Create a new course in the database."""
        course: Course = Course(**course_schema.model_dump())
        self.session.add(course)
        await self.session.flush()
        return course

    async def get_course(
        self,
        course_id: uuid.UUID,
    ) -> Course | None:
        """Get a course by its ID."""
        query: Select[Any] = select(Course).where(
            and_(Course.id == course_id, Course.is_active)
        )
        result: Result[Any] = await self.session.execute(query)
        return result.scalar_one_or_none()
