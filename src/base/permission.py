import logging
from abc import abstractmethod
from typing import TypedDict, Unpack

from fastapi.requests import Request

from src.courses.models import Course
from src.lessons.models import Lesson
from src.users import Author, User

logger = logging.getLogger(__name__)


class PermissionKwargs(TypedDict, total=False):
    """TypedDict for keyword arguments passed to permission classes.

    Attributes:
        user (User | None): The current authenticated user.
        target_user (User): Target user for permission checks.
        author (Author | None): The current author.
        course (Course): Target course for permission checks.
        lesson (Lesson): Target lesson for permission checks.

    """

    user: User | None
    target_user: User
    author: Author | None
    course: Course
    lesson: Lesson


class BasePermission:
    """Abstract base class for all permission classes.

    Provides a base structure for permission validation and stores
    the current request context.
    """

    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        """Initialize the base permission.

        Args:
            request (Request): The current HTTP request.
            **kwargs (PermissionKwargs): Optional keyword arguments
                relevant to permission checks.

        """
        self.request: Request = request

    @abstractmethod
    async def validate_permission(self) -> None:
        """Validate that the current request has permission to proceed.

        Raises:
            Exception: Subclasses should raise an appropriate exception
                if permission is denied.

        """
        ...
