from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Security

from src.base.dependencies import get_service
from src.courses.dependencies import CoursePermissionDependency
from src.courses.models import Course
from src.courses.permissions import IsAuthorCourse
from src.lessons.schemas import CreateLessonRequestSchema, LessonResponseSchema
from src.lessons.service import LessonService

lesson_router = APIRouter()


@lesson_router.post('/{course_id}', response_model=LessonResponseSchema)
async def create_lesson(
    lesson_schema: CreateLessonRequestSchema,
        course: Annotated[
            Course,
            Security(
                CoursePermissionDependency(
                    [
                        IsAuthorCourse
                    ],
                )
            )
        ],
    service: Annotated[LessonService, Depends(get_service(LessonService))],
) -> LessonResponseSchema:
    lesson = await service.create_lesson(
        course=course, lesson_schema=lesson_schema
    )
    return LessonResponseSchema.model_validate(lesson)
