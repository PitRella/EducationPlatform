import uuid
from typing import Annotated

from fastapi import Depends

from src.base.dependencies import get_service
from src.courses.models import Course
from src.courses.service import CourseService

async def get_course_by_id(
        course_id: uuid.UUID,
        service: Annotated[CourseService, Depends(get_service(CourseService))]
) -> Course:
    """Dependency function to retrieve a course by its ID.

    Args:
        course_id (uuid.UUID): The unique ID of the course to retrieve.
        service (CourseService): The course service instance for db operations.

    Returns:
        Course: The course object if found.

    Raises:
        HTTPException: If the course is not found or other database errors.
    """

    return await service.get_course(course_id)

