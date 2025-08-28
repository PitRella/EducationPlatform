from abc import ABC
from typing import Unpack

from fastapi.requests import Request
from src.base.permission import BasePermission, PermissionKwargs
from src.lessons.exceptions import LessonIsNotPublishedException
from src.users.permissions import BaseAuthorPermission


class BaseLessonPermission(BasePermission, ABC):
    """Abstract base class for lesson-related permissions.

    Provides access to the lesson object from dependency kwargs so that
    permission checks can be implemented in subclasses.
    """

    def __init__(
            self,
            request: Request,
            **kwargs: Unpack[PermissionKwargs],
    ):
        """Initialize the base lesson permission.

        Args:
            request (Request): The current HTTP request.
            **kwargs (PermissionKwargs): Additional keyword arguments
                including the lesson instance.
        """
        super().__init__(request, **kwargs)
        self.lesson = kwargs['lesson']


class BaseAuthorLessonPermission(
    BaseLessonPermission,
    BaseAuthorPermission,
    ABC
):
    """Abstract base class for permissions requiring lesson and author.

    Inherits from both BaseLessonPermission and BaseAuthorPermission.
    Useful for checks that require both author identity and lesson context.
    """

    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        """Initialize the base author lesson permission.

        Args:
            request (Request): The current HTTP request.
            **kwargs (PermissionKwargs): Additional keyword arguments
                including the lesson and author context.
        """
        super().__init__(request, **kwargs)


class IsLessonPublished(BaseLessonPermission):
    """Permission that checks whether a lesson is published."""

    async def validate_permission(self) -> None:
        """Validate that the lesson is published.

        Raises:
            LessonIsNotPublishedException: If the lesson is not published.
        """
        if self.lesson.is_published:
            return None  # If published, everyone can access it
        raise LessonIsNotPublishedException


class IsLessonAuthor(BaseAuthorLessonPermission):
    """Permission that checks whether the current author owns the lesson."""

    async def validate_permission(self) -> None:
        """Validate that the current author is the lesson's owner.

        Raises:
            LessonIsNotPublishedException: If the author is not the lesson
                owner, and the lesson is unpublished.
        """
        author = self._is_author_authorized()
        if self.lesson.course.author_id == author.id:
            return None  # Author can access unpublished lessons
        raise LessonIsNotPublishedException
