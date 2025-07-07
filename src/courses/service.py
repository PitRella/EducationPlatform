from sqlalchemy.ext.asyncio import AsyncSession

from src.courses.dao import AbstractCourseDAO, CourseDAO
from src.courses.models import Course
from src.courses.schemas import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
)


class CourseService:
    """Service class for handling course-related business logic."""

    def __init__(
        self,
        db_session: AsyncSession,
        dao: AbstractCourseDAO | None = None,
    ) -> None:
        """Initialize a new UserService instance.

        Args:
            db_session (AsyncSession): The SQLAlchemy async session
            dao (UserDAO | None, optional): Data Access Object
             for user operations.
                If None, creates a new UserDAO instance.
                Defaults to None.

        """
        self._session: AsyncSession = db_session
        self._dao: AbstractCourseDAO = dao or CourseDAO(db_session)

    @property
    def session(self) -> AsyncSession:
        """Return the current SQLAlchemy session."""
        return self._session

    @property
    def dao(self) -> AbstractCourseDAO:
        """Return current course DAO."""
        return self._dao

    async def create_course(
        self, course_schema: CreateCourseRequestSchema
    ) -> CreateCourseResponseSchema:
        """Create a new course in the database."""
        async with self.session.begin():
            course: Course = await self.dao.create_course(course_schema)
        return CreateCourseResponseSchema.model_validate(course)
