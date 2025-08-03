import uuid
from typing import Annotated

from fastapi import Depends

from src.auth.dependencies import get_user_from_jwt
from src.base.dependencies import get_service
from src.courses.models import Course
from src.courses.service import CourseService
from src.users import Author, User
from src.users.dependencies import get_author_from_jwt
from src.users.models import UserCourses
from src.users.services.user_courses import UserCoursesService


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


async def get_author_course_by_id(
        course_id: uuid.UUID,
        author: Annotated[Author, Depends(get_author_from_jwt)],
        service: Annotated[CourseService, Depends(get_service(CourseService))]
) -> Course:
    return await service.get_author_course(
        course_id=course_id,
        author=author
    )

async def is_user_bought_course(
        course_id: uuid.UUID,
        user: Annotated[User, Depends(get_user_from_jwt)],
        service: Annotated[UserCoursesService, Depends(get_service(UserCoursesService))]
) -> UserCourses:
    return await service.user_bought_course(user=user, course_id=course_id)