import uuid
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.service import BaseService
from src.courses.models import Course

from src.lessons.dao import LessonDAO
from src.lessons.exceptions import LessonIsNotPublishedException, \
    LessonNotFoundByIdException
from src.lessons.models import Lesson
from src.lessons.schemas import CreateLessonRequestSchema, \
    UpdateLessonRequestSchema
from src.utils import make_slug


class LessonService(BaseService):
    _DEACTIVATE_LESSON_UPDATE: ClassVar[dict[str, bool]] = {
        'is_published': False
    }

    def __init__(
            self,
            db_session: AsyncSession,
            dao: LessonDAO | None = None,
    ) -> None:
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
        filtered_lesson_fields: dict[str, str] = (
            self._validate_schema_for_update_request(lesson_fields)
        )
        lesson_title = filtered_lesson_fields.get('title')
        if lesson_title: # If title changed - change slug
                filtered_lesson_fields['slug'] = make_slug(lesson_title)
        async with self.session.begin():
            updated_lesson: Lesson | None = await self._dao.update(
                filtered_lesson_fields, id=lesson.id,
            )
        if not updated_lesson:
            raise LessonNotFoundByIdException
        return updated_lesson
