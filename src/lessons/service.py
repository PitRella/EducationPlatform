import uuid
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.service import BaseService
from src.courses.models import Course

from src.lessons.dao import LessonDAO
from src.lessons.exceptions import (
    LessonIsNotPublishedException,
    LessonNotFoundByIdException
)
from src.lessons.models import Lesson
from src.lessons.schemas import (
    CreateLessonRequestSchema,
    UpdateLessonRequestSchema
)
from src.utils import make_slug


class LessonService(BaseService):
    """Service layer for managing lessons.

    Provides methods to create, retrieve, update, and deactivate lessons.
    All operations are performed using the LessonDAO and within the given
    database session.
    """

    _DEACTIVATE_LESSON_UPDATE: ClassVar[dict[str, bool]] = {
        'is_published': False
    }

    def __init__(
            self,
            db_session: AsyncSession,
            dao: LessonDAO | None = None,
    ) -> None:
        """Initialize the LessonService.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session.
            dao (LessonDAO | None): Optional data access object for lessons.
                If not provided, a new LessonDAO is created.
        """
        super().__init__(db_session)
        self._dao: LessonDAO = dao or LessonDAO(
            db_session,
            Lesson,
        )

    async def create_lesson(
            self,
            course: Course,
            lesson_schema: CreateLessonRequestSchema,
    ) -> Lesson:
        """Create a new lesson in the given course.

        The lesson slug is automatically generated from the title. The lesson
        is stored in the database within a transaction.

        Args:
            course (Course): The course to which the lesson belongs.
            lesson_schema (CreateLessonRequestSchema): Schema with lesson
                creation data.

        Returns:
            Lesson: The created lesson instance.
        """
        lesson_data = lesson_schema.model_dump()
        lesson_data['course_id'] = course.id
        lesson_data['slug'] = make_slug(lesson_data.get('title'))
        async with self.session.begin():
            lesson: Lesson = await self._dao.create(lesson_data)
        return lesson

    async def get_lesson(
            self,
            lesson_id: uuid.UUID,
    ) -> Lesson:
        """Retrieve a lesson with its associated course by ID.

        Args:
            lesson_id (uuid.UUID): Unique identifier of the lesson.

        Returns:
            Lesson: The lesson instance with its course loaded.

        Raises:
            LessonIsNotPublishedException: If the lesson does not exist or is
                not published.
        """
        async with self.session.begin():
            lesson: Lesson | None = await self._dao.get_lesson_with_course(
                id=lesson_id
            )
        if not lesson:
            raise LessonIsNotPublishedException
        return lesson

    async def deactivate_lesson(
            self,
            lesson: Lesson,
    ) -> None:
        """Deactivate a lesson by marking it as unpublished.

        Args:
            lesson (Lesson): The lesson instance to deactivate.

        Raises:
            LessonNotFoundByIdException: If the lesson cannot be found.
        """
        async with self.session.begin():
            updated_lesson: Lesson | None = await self._dao.update(
                self._DEACTIVATE_LESSON_UPDATE,
                id=lesson.id,
            )
        if not updated_lesson:
            raise LessonNotFoundByIdException

    async def update_lesson(
            self,
            lesson: Lesson,
            lesson_fields: UpdateLessonRequestSchema,
    ) -> Lesson:
        """Update fields of an existing lesson.

        If the lesson title is updated, the slug will be regenerated.

        Args:
            lesson (Lesson): The lesson instance to update.
            lesson_fields (UpdateLessonRequestSchema): Schema with updated
                fields.

        Returns:
            Lesson: The updated lesson instance.

        Raises:
            LessonNotFoundByIdException: If the lesson cannot be found.
        """
        filtered_lesson_fields: dict[str, str] = (
            self._validate_schema_for_update_request(lesson_fields)
        )
        lesson_title = filtered_lesson_fields.get('title')
        if lesson_title:  # If title changed - change slug
            filtered_lesson_fields['slug'] = make_slug(lesson_title)
        async with self.session.begin():
            updated_lesson: Lesson | None = await self._dao.update(
                filtered_lesson_fields, id=lesson.id,
            )
        if not updated_lesson:
            raise LessonNotFoundByIdException
        return updated_lesson
