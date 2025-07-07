from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.courses.models import Course
from src.courses.schemas import (
    CreateCourseRequestSchema,
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
        self, course_schema: CreateCourseRequestSchema
    ) -> Course:
        """Create a new course in the database."""
        raise NotImplementedError


class CourseDAO(AbstractCourseDAO):
    """Course Data Access Object."""

    async def create_course(
        self, course_schema: CreateCourseRequestSchema
    ) -> Course:
        """Create a new course in the database."""
        course: Course = Course(**course_schema.model_dump())
        self.session.add(course)
        await self.session.flush()
        return course
