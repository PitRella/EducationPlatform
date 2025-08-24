import uuid
from typing import Annotated

from fastapi import Depends

from src.base.dependencies import get_service
from src.lessons.models import Lesson
from src.lessons.service import LessonService


async def _get_lesson_by_id(
        lesson_id: uuid.UUID,
        service: Annotated[LessonService, Depends(get_service(LessonService))],
) -> Lesson:
    return await service.get_lesson(lesson_id)