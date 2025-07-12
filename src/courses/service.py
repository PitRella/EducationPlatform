import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.courses.exceptions import CourseNotFoundByIdException
from src.courses.models import Course
from src.courses.schemas import (
    BaseCourseResponseSchema,
    BaseCreateCourseSchema,
)

type CourseDAO = BaseDAO[Course, BaseCreateCourseSchema]


class CourseService(BaseService):
    """Service class for handling course-related business logic."""

    def __init__(
        self,
        db_session: AsyncSession,
        dao: CourseDAO | None = None,
    ) -> None:
        """Initialize a new UserService instance.

        Args:
            db_session (AsyncSession): The SQLAlchemy async session
            dao (UserDAO | None, optional): Data Access Object
             for user operations.
                If None, creates a new UserDAO instance.
                Defaults to None.

        """
        super().__init__(db_session)
        self._dao: CourseDAO = dao or BaseDAO[Course, BaseCreateCourseSchema](
            db_session,
            Course,
        )

    @property
    def dao(self) -> CourseDAO:
        """Return current course DAO."""
        return self._dao

    async def create_course(
        self, course_schema: BaseCreateCourseSchema
    ) -> BaseCourseResponseSchema:
        """Create a new course in the database."""
        async with self.session.begin():
            course: Course = await self.dao.create(course_schema)
        return BaseCourseResponseSchema.model_validate(course)

    async def get_course(
        self,
        course_id: uuid.UUID,
    ) -> BaseCourseResponseSchema:
        """Get a course by its ID."""
        async with self.session.begin():
            course: Course | None = await self.dao.get_one(id=course_id)
        if not course:
            raise CourseNotFoundByIdException
        return BaseCourseResponseSchema.model_validate(course)
