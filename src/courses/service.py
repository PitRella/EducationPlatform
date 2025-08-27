import datetime as dt
import uuid
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.courses.dao import CourseDAO
from src.courses.exceptions import CourseNotFoundByIdException, \
    CourseWasNotBoughtException
from src.courses.models import Course
from src.courses.schemas import (
    BaseCreateCourseRequestSchema,
    UpdateCourseRequestSchema,
)
from src.users import User
from src.users.models import Author
from src.utils import make_slug
from src.users.models import UserCourses

type UserCourseDAO = BaseDAO[UserCourses]


class CourseService(BaseService):
    """Service class for handling course-related business logic."""

    _DEACTIVATE_COURSE_UPDATE: ClassVar[dict[str, bool]] = {'is_active': False}

    def __init__(
            self,
            db_session: AsyncSession,
            course_dao: CourseDAO | None = None,
            user_courses_dao: UserCourseDAO | None = None,
    ) -> None:
        """Initialize a new UserService instance.

        Args:
            db_session (AsyncSession): The SQLAlchemy async session
            course_dao (UserDAO | None, optional): Data Access Object
             for user operations.
                If None, creates a new UserDAO instance.
                Defaults to None.

        """
        super().__init__(db_session)
        self._course_dao: CourseDAO = course_dao or CourseDAO(
            db_session,
            Course,
        )
        self._user_courses_dao: UserCourseDAO = user_courses_dao or BaseDAO[
            UserCourses
        ](db_session, model=UserCourses)

    async def create_course(
            self, author: Author, course_schema: BaseCreateCourseRequestSchema
    ) -> Course:
        """Create a new course in the database."""
        course_data = course_schema.model_dump()
        course_data['author_id'] = author.id
        course_data['slug'] = make_slug(course_data.get('title'))
        async with self.session.begin():
            course: Course = await self._course_dao.create(course_data)
        return course

    async def get_course(
            self,
            course_id: uuid.UUID,
            author: Author | None = None,
    ) -> Course:
        filters = {'id': course_id}
        if author:
            filters['author_id'] = author.id
        async with self.session.begin():
            course: Course | None = await self._course_dao.get_course_with_lessons(
                **filters,
            )
        if not course:
            raise CourseNotFoundByIdException
        return course

    async def update_course(
            self,
            course: Course,
            course_fields: UpdateCourseRequestSchema,
    ) -> Course:
        filtered_course_fields: dict[str, str] = (
            self._validate_schema_for_update_request(course_fields)
        )
        if course_fields.title:
            filtered_course_fields['slug'] = make_slug(
                filtered_course_fields.get('title')
            )
        async with self.session.begin():
            updated_course: Course | None = await self._course_dao.update(
                filtered_course_fields, id=course.id,
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
            courses: list[Course] | None = await self._course_dao.get_all(
                created_at=created_at,
                last_id=last_id,
                limit=limit,
                order_by=['rating'],
                is_active=True,
            )
        return courses if courses else []

    async def deactivate_course(
            self,
            course: Course,
    ) -> None:
        async with self.session.begin():
            deleted_course: Course | None = await self._course_dao.update(
                self._DEACTIVATE_COURSE_UPDATE,
                id=course.id,
            )
        if not deleted_course:
            raise CourseNotFoundByIdException

    async def purchase_course(
            self,
            course: Course,
            user: User,
    ) -> None:
        async with self.session.begin():
            bought_course: UserCourses | None = await self._user_courses_dao.create(
                {
                    "user_id": user.id,
                    "course_id": course.id
                }
            )
        if not bought_course:
            raise CourseWasNotBoughtException
