import uuid
from collections.abc import Sequence
from typing import Annotated, Literal

from fastapi import Depends
from fastapi.requests import Request

from src.base.dependencies import BasePermissionDependency, get_service
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
    """Dependency class for validating course-related permissions.

    This dependency checks if the given author has the required
    permissions to access or modify a course. Multiple permission checks
    can be combined with logical operators (AND/OR).
    """

    def __init__(
        self,
        permissions: Sequence[type[BaseCoursePermission]],
        logic: Literal['AND', 'OR'] = BasePermissionDependency._LOGIC_AND,
    ):
        """Initialize the course permission dependency.

        Args:
            permissions (Sequence[type[BaseCoursePermission]]): A sequence of
                course permission classes to validate.
            logic (Literal["AND", "OR"]): Logical operator to combine multiple
                permission checks. Defaults to "AND".

        """
        super().__init__(permissions, logic)

    async def __call__(
        self,
        request: Request,
        author: Annotated[
            Author | None, Depends(_get_optional_author_from_jwt)
        ],
        course: Annotated[Course, Depends(_get_course_by_id)],
    ) -> Course:
        """Validate permissions for accessing or modifying a course.

        This method is invoked as a FastAPI dependency. It ensures that
        the current author has the required permissions for the given
        course.

        Args:
            request (Request): The current HTTP request.
            author (Author | None): The author extracted from the JWT, if any.
            course (Course): The course retrieved from the request context.

        Returns:
            Course: The validated course instance.

        Raises:
            HTTPException: If the author does not have the required
                permissions.

        """
        await self._validate_permissions(
            request=request, author=author, course=course
        )
        return course
