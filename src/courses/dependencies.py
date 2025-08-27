import uuid
from typing import Annotated, Sequence, Literal

from fastapi import Depends
from fastapi.requests import Request

from src.base.dependencies import get_service, BasePermissionDependency
from src.courses.models import Course
from src.courses.permissions import BaseCoursePermission
from src.courses.service import CourseService
from src.users import Author
from src.users.dependencies.author import _get_optional_author_from_jwt


async def _get_course_by_id(
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


class CoursePermissionDependency(BasePermissionDependency):
    def __init__(
            self,
            permissions: Sequence[type[BaseCoursePermission]],
            logic: Literal["AND", "OR"] = BasePermissionDependency._LOGIC_AND
    ):
        super().__init__(permissions, logic)

    async def __call__(
            self,
            request: Request,
            author: Annotated[
                Author | None,
                Depends(_get_optional_author_from_jwt)
            ],
            course: Annotated[Course, Depends(_get_course_by_id)],
    ) -> Course:
        await self._validate_permissions(
            request=request,
            author=author,
            course=course
        )
        return course
