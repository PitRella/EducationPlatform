from typing import Annotated

from fastapi import APIRouter, Depends

from src.base.dependencies import get_service
from src.courses.dependencies import get_author_course_by_id
from src.courses.models import Course
from src.lessons.schemas import LessonResponseSchema, CreateLessonRequestSchema
from src.lessons.service import LessonService

lesson_router = APIRouter()

@lesson_router.post('/{course_id}', response_model=LessonResponseSchema)
async def create_lesson(
    lesson_schema: CreateLessonRequestSchema,
    course: Annotated[Course, Depends(get_author_course_by_id)],
    service: Annotated[LessonService, Depends(get_service(LessonService))],
) -> LessonResponseSchema:
    """Endpoint to create a new course."""
    lesson = await service.create_lesson(course=course, lesson_schema=lesson_schema)
    return LessonResponseSchema.model_validate(lesson)