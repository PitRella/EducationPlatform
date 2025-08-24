import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.service import BaseService
from src.courses.models import Course

from src.lessons.dao import LessonDAO
from src.lessons.exceptions import LessonIsNotPublishedException
from src.lessons.models import Lesson
from src.lessons.schemas import CreateLessonRequestSchema
from src.utils import make_slug


class LessonService(BaseService):
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
