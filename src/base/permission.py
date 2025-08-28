import logging
from abc import abstractmethod
from typing import TypedDict, Unpack

from fastapi.requests import Request

from src.courses.models import Course
from src.lessons.models import Lesson
from src.users import Author, User

logger = logging.getLogger(__name__)


class PermissionKwargs(TypedDict, total=False):
    user: User | None
    target_user: User
    author: Author | None
    course: Course
    lesson: Lesson


class BasePermission:
    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        # The current HTTP request
        self.request: Request = request

    @abstractmethod
    async def validate_permission(
        self,
    ) -> None:
        """Abstract method that must be implemented by all permission classes.

        Should raise an exception if the permission check fails.
        """
        ...
