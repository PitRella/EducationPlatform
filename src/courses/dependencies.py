import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from src.auth.dependencies import get_user_from_jwt, get_optional_user_from_jwt
from src.base.dependencies import get_service
from src.courses.models import Course
from src.courses.permissions import CoursePermission
from src.courses.service import CourseService
from src.users import Author, User
from src.users.dependencies import get_author_from_jwt


async def get_course_by_id(
    course_id: uuid.UUID,
    service: Annotated[CourseService, Depends(get_service(CourseService))],
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
    service: Annotated[CourseService, Depends(get_service(CourseService))],
) -> Course:
    return await service.get_author_course(course_id=course_id, author=author)


class CoursePermissionDependency:
    def __init__(self, permissions: list[type[CoursePermission]]):
        self.permissions = permissions

    async def __call__(
        self,
        request: Request,
        user: Annotated[User | None, Depends(get_optional_user_from_jwt)],
        course: Annotated[Course, Depends(get_course_by_id)],
    ) -> Course:
        for permission_cls in self.permissions:
            p_class = permission_cls(request=request, user=user, course=course)
            await p_class.validate_permission()
        return course
