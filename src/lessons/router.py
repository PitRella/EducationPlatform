import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Security

from src.base.dependencies import get_service
from src.courses.dependencies import CoursePermissionDependency
from src.courses.models import Course
from src.courses.permissions import IsAuthorCourse, IsCourseActive
from src.lessons.dependencies import LessonPermissionDependency
from src.lessons.models import Lesson
from src.lessons.permissions import IsLessonPublished, IsLessonAuthor
from src.lessons.schemas import CreateLessonRequestSchema, \
    LessonResponseSchema, UpdateLessonRequestSchema
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
    lesson: Lesson = await service.create_lesson(
        course=course, lesson_schema=lesson_schema
    )
    return LessonResponseSchema.model_validate(lesson)


@lesson_router.get('/{lesson_id}', response_model=LessonResponseSchema)
async def get_lesson(
        lesson: Annotated[
            Lesson,
            Security(
                LessonPermissionDependency(
                    [
                        IsLessonPublished,
                        IsLessonAuthor,
                    ],
                    logic="OR"
                )
            )
        ]
) -> LessonResponseSchema:
    return LessonResponseSchema.model_validate(lesson)

@lesson_router.delete('/{lesson_id}', status_code=204)
async def deactivate_lesson_by_id(
        lesson: Annotated[
            Lesson,
            Security(
                LessonPermissionDependency(
                    [
                        IsLessonAuthor
                    ],
                )
            )
        ],
        service: Annotated[LessonService, Depends(get_service(LessonService))],
) -> None:
    await service.deactivate_lesson(lesson=lesson)

@lesson_router.patch('/{lesson_id}', response_model=LessonResponseSchema)
async def update_lesson(
        lesson_fields: UpdateLessonRequestSchema,
        lesson: Annotated[
            Lesson,
            Security(
                LessonPermissionDependency(
                    [
                        IsLessonAuthor
                    ],
                )
            )
        ],
        service: Annotated[LessonService, Depends(get_service(LessonService))],
) -> LessonResponseSchema:
    updated_lesson: Lesson = await service.update_lesson(
        lesson=lesson, lesson_fields=lesson_fields
    )
    return LessonResponseSchema.model_validate(updated_lesson)