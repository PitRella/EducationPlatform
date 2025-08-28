from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Security

from src.base.dependencies import get_service
from src.courses.dependencies import CoursePermissionDependency
from src.courses.models import Course
from src.courses.permissions import IsAuthorCourse
from src.lessons.dependencies import LessonPermissionDependency
from src.lessons.models import Lesson
from src.lessons.permissions import IsLessonPublished, IsLessonAuthor
from src.lessons.schemas import (
    CreateLessonRequestSchema,
    LessonResponseSchema,
    UpdateLessonRequestSchema
)
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
    """Create a new lesson in the specified course.

    Only the course author can create a lesson. The lesson is stored in the
    database and returned as a validated schema.

    Args:
        lesson_schema (CreateLessonRequestSchema): Schema with lesson data.
        course (Course): The course instance is validated by permission checks.
        service (LessonService): Service for managing lesson operations.

    Returns:
        LessonResponseSchema: Schema representation of the created lesson.
    """
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
    """Retrieve a lesson by its ID.

    A lesson can be retrieved if it is published, or if the requester is
    the author of the lesson.

    Args:
        lesson (Lesson): The lesson instance validated by permission checks.

    Returns:
        LessonResponseSchema: Schema representation of the lesson.
    """
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
    """Deactivate a lesson by its ID.

    Only the author of the lesson can deactivate it. Deactivation marks
    the lesson as unpublished.

    Args:
        lesson (Lesson): The lesson instance validated by permission checks.
        service (LessonService): Service for managing lesson operations.

    Returns:
        None
    """
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
    """Update an existing lesson by its ID.

    Only the author of the lesson can update it. If the title changes, the
    slug will be regenerated.

    Args:
        lesson_fields (UpdateLessonRequestSchema): Schema with updated data.
        lesson (Lesson): The lesson instance validated by permission checks.
        service (LessonService): Service for managing lesson operations.

    Returns:
        LessonResponseSchema: Schema representation of the updated lesson.
    """
    updated_lesson: Lesson = await service.update_lesson(
        lesson=lesson, lesson_fields=lesson_fields
    )
    return LessonResponseSchema.model_validate(updated_lesson)
