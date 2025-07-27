import datetime as dt
import uuid
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.courses.exceptions import CourseNotFoundByIdException
from src.courses.models import Course
from src.courses.schemas import (
    BaseCreateCourseRequestSchema,
    UpdateCourseRequestSchema,
)
from src.users.models import Author
from src.utils import make_slug

type CourseDAO = BaseDAO[Course, BaseCreateCourseRequestSchema]


class CourseService(BaseService):
    """Service class for handling course-related business logic."""

    _DEACTIVATE_COURSE_UPDATE: ClassVar[dict[str, bool]] = {'is_active': False}

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
            Course, BaseCreateCourseRequestSchema
        ](
            db_session,
            Course,
        )

    @property
    def dao(self) -> CourseDAO:
        """Return current course DAO."""
        return self._dao

    async def create_course(
        self, author: Author, course_schema: BaseCreateCourseRequestSchema
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
        """Retrieve a course by its ID from the database.

        Args:
            course_id (uuid.UUID): The unique ID of the course to retrieve.

        Returns:
            Course: The course object if found and active.

        Raises:
            CourseNotFoundByIdException: If no active course is found
                with the given ID.

        """
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
        course_fields: UpdateCourseRequestSchema,
    ) -> Course:
        """Update an existing course by ID and author with the provided fields.

        Args:
            course_id (uuid.UUID): The ID of the course to update.
            author (Author): The author of the course.
            course_fields (UpdateCourseRequestSchema): Fields to update.

        Returns:
            Course: The updated course instance.

        Raises:
            CourseNotFoundByIdException: If the course does not exist.

        """
        filtered_course_fields: dict[str, str] = (
            self._validate_schema_for_update_request(course_fields)
        )
        if course_fields.title:
            filtered_course_fields['slug'] = make_slug(
                filtered_course_fields.get('title')
            )
        async with self.session.begin():
            updated_course: Course | None = await self.dao.update(
                filtered_course_fields, id=course_id, author_id=author.id
            )
        if not updated_course:
            raise CourseNotFoundByIdException
        return updated_course

    async def get_all_courses(
        self,
        created_at: dt.datetime | None = None,
        last_id: uuid.UUID | None = None,
        limit: int | None = None,
    ) -> list[Course]:
        """Retrieve a list of all active courses from the database.

        Args:
            created_at (dt.datetime | None, optional): Filter courses created
                after this timestamp. Defaults to None.
            last_id (uuid.UUID | None, optional): Last course ID for paginating.
                Defaults to None.
            limit (int | None, optional): Maximum number of courses to return.
                Defaults to None.

        Returns:
            list[Course]: List of active courses, ordered by rating.
            Returns an empty list if no courses found.

        """
        async with self.session.begin():
            courses: list[Course] | None = await self.dao.get_all(
                created_at=created_at,
                last_id=last_id,
                limit=limit,
                order_by=['rating'],
                is_active=True,
            )
        return courses if courses else []

    async def deactivate_course(
        self,
        course_id: uuid.UUID,
        author: Author,
    ) -> None:
        """Deactivate a course in the database.

        Args:
            course_id (uuid.UUID): The ID of the course to deactivate.
            author (Author): The author of the course.

        Raises:
            CourseNotFoundByIdException: If the course does not exist or
                does not belong to the specified author.

        Note:
            This operation sets the course's is_active flag to False.

        """
        async with self.session.begin():
            deleted_course: Course | None = await self.dao.update(
                self._DEACTIVATE_COURSE_UPDATE,
                id=course_id,
                author_id=author.id,
            )
        if not deleted_course:
            raise CourseNotFoundByIdException
