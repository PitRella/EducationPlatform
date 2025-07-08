import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from src.courses.dependencies import get_service
from src.courses.schemas import (
    BaseCourseResponseSchema,
    BaseCreateCourseSchema,
)
from src.courses.service import CourseService

course_router = APIRouter()


@course_router.post('/', response_model=BaseCourseResponseSchema)
async def create_course(
    course_schema: BaseCreateCourseSchema,
    service: Annotated[CourseService, Depends(get_service)],
) -> BaseCourseResponseSchema:
    """Endpoint to create a new course."""
    return await service.create_course(course_schema)


@course_router.get('/', response_model=BaseCourseResponseSchema)
async def get_course(
    course_id: uuid.UUID,
    service: Annotated[CourseService, Depends(get_service)],
) -> BaseCourseResponseSchema:
    """Endpoint to get a course by its ID."""
    return await service.get_course(course_id)
