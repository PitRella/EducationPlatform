import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.courses.exceptions import CourseNotFoundByIdException
from src.courses.models import Course
from src.courses.schemas import (
    BaseCreateCourseRequestSchema, UpdateCourseRequestSchema,
)
from src.users.models import Author
from src.utils import make_slug

type CourseDAO = BaseDAO[Course, BaseCreateCourseRequestSchema]


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
        self._dao: CourseDAO = dao or BaseDAO[
            Course, BaseCreateCourseRequestSchema](
            db_session,
            Course,
        )

    @property
    def dao(self) -> CourseDAO:
        """Return current course DAO."""
        return self._dao

    async def create_course(
            self,
            author: Author,
            course_schema: BaseCreateCourseRequestSchema
    ) -> Course:
        """Create a new course in the database."""
        course_data = course_schema.model_dump()
        course_data['author_id'] = author.id
        course_data['slug'] = make_slug(course_data.get('title'))
        async with self.session.begin():
            course: Course = await self.dao.create(course_data)
        return course

    async def get_course(
            self,
            course_id: uuid.UUID,
    ) -> Course:
        """Get a course by its ID."""
        async with self.session.begin():
            course: Course | None = await self.dao.get_one(
                id=course_id,
                is_active=True,
            )
        if not course:
            raise CourseNotFoundByIdException
        return course

    async def update_course(
            self,
            course_id: uuid.UUID,
            author: Author,
            course_fields: UpdateCourseRequestSchema
    ):
        filtered_course_fields: dict[
            str, str] = self._validate_schema_for_update_request(course_fields)
        async with self.session.begin():
            updated_course: Course | None = await self.dao.update(
                filtered_course_fields, id=course_id, author_id=author.id)
        if not updated_course:
            raise CourseNotFoundByIdException
        return updated_course
