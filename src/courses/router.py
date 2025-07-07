from typing import Annotated

from fastapi import APIRouter, Depends

from src.courses.dependencies import get_service
from src.courses.schemas import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
)
from src.courses.service import CourseService

course_router = APIRouter()


@course_router.post('/', response_model=CreateCourseResponseSchema)
async def create_course(
    course_schema: CreateCourseRequestSchema,
    service: Annotated[CourseService, Depends(get_service)],
) -> CreateCourseResponseSchema:
    """Endpoint to create a new course."""
    return await service.create_course(course_schema)
