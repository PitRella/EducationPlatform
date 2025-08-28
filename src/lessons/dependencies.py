import uuid
from collections.abc import Sequence
from typing import Annotated, Literal

from fastapi import Depends
from fastapi.requests import Request

from src.base.dependencies import BasePermissionDependency, get_service
from src.lessons.models import Lesson
from src.lessons.permissions import BaseLessonPermission
from src.lessons.service import LessonService
from src.users import Author
from src.users.dependencies.author import _get_optional_author_from_jwt


async def _get_lesson_by_id(
    lesson_id: uuid.UUID,
    service: Annotated[LessonService, Depends(get_service(LessonService))],
) -> Lesson:
    return await service.get_lesson(lesson_id)

class LessonPermissionDependency(BasePermissionDependency):
    """Dependency class for validating lesson-related permissions.

    This dependency checks whether the given author has the required
    permissions to access or modify a lesson. It uses logical operators
    (AND/OR) to combine multiple permission checks.
    """

    def __init__(
        self,
        permissions: Sequence[type[BaseLessonPermission]],
        logic: Literal['AND', 'OR'] = BasePermissionDependency._LOGIC_AND,
    ):
        """Initialize the LessonPermissionDependency.

        Args:
            permissions (Sequence[type[BaseLessonPermission]]): A sequence of
                permission classes to validate against.
            logic (Literal['AND', 'OR']): Logical operator that defines how
                multiple permissions are combined. Defaults to 'AND'.
        """
        super().__init__(permissions, logic)

    async def __call__(
        self,
        request: Request,
        author: Annotated[
            Author | None, Depends(_get_optional_author_from_jwt)
        ],
        lesson: Annotated[Lesson, Depends(_get_lesson_by_id)],
    ) -> Lesson:
        """Validate permissions for accessing or modifying a lesson.

        This method is invoked as a FastAPI dependency. It ensures that the
        author has the required permissions for the given lesson.

        Args:
            request (Request): The incoming HTTP request.
            author (Author | None): The author extracted from the JWT, if any.
            lesson (Lesson): The lesson retrieved from the request context.

        Returns:
            Lesson: The validated lesson instance.

        Raises:
            HTTPException: If the author does not have the required
                permissions.
        """
        await self._validate_permissions(
            request=request,
            lesson=lesson,
            author=author,
        )
        return lesson
