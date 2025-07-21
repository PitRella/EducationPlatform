import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from src.base.dependencies import get_service
from src.courses.schemas import (
    BaseCourseResponseSchema,
    BaseCreateCourseRequestSchema, UpdateCourseRequestSchema,
)
from src.courses.service import CourseService
from src.users.dependencies.author import get_author_from_jwt
from src.users.models import Author

course_router = APIRouter()


@course_router.post('/', response_model=BaseCourseResponseSchema)
async def create_course(
        course_schema: BaseCreateCourseRequestSchema,
        author: Annotated[Author, Depends(get_author_from_jwt)],
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> BaseCourseResponseSchema:
    """Endpoint to create a new course."""
    course = await service.create_course(
        author=author,
        course_schema=course_schema
    )
    return BaseCourseResponseSchema.model_validate(course)


@course_router.get('/{course_id}', response_model=BaseCourseResponseSchema)
async def get_course(
        course_id: uuid.UUID,
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> BaseCourseResponseSchema:
    """Endpoint to get a course by its ID."""
    course = await service.get_course(course_id)
    return BaseCourseResponseSchema.model_validate(course)


@course_router.patch('/{course_id}', response_model=BaseCourseResponseSchema)
async def update_course(
        course_id: uuid.UUID,
        course_fields: UpdateCourseRequestSchema,
        author: Annotated[Author, Depends(get_author_from_jwt)],
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> BaseCourseResponseSchema:
    updated_course = await service.update_course(course_id=course_id, author=author,
                                           course_fields=course_fields)
    return BaseCourseResponseSchema.model_validate(updated_course)
