import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from src.base.dependencies import get_service
from src.courses.schemas import (
    BaseCourseResponseSchema,
    BaseCreateCourseSchema,
)
from src.courses.service import CourseService
from src.users.dependencies.author import get_author_from_jwt
from src.users.models import Author

course_router = APIRouter()


@course_router.post('/', response_model=BaseCourseResponseSchema)
async def create_course(
        course_schema: BaseCreateCourseSchema,
        author: Annotated[Author, Depends(get_author_from_jwt)],
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> BaseCourseResponseSchema:
    """Endpoint to create a new course."""
    return await service.create_course(author=author, course_schema = course_schema)


@course_router.get('/{course_id}', response_model=BaseCourseResponseSchema)
async def get_course(
        course_id: uuid.UUID,
        service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> BaseCourseResponseSchema:
    """Endpoint to get a course by its ID."""
    return await service.get_course(course_id)
