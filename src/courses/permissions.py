from abc import ABC
from typing import Unpack

from fastapi.requests import Request

from src.base.permission import BasePermission, PermissionKwargs
from src.users.exceptions import UserPermissionException
from src.users.permissions import BaseAuthorPermission


class BaseCoursePermission(BasePermission, ABC):
    """Abstract base class for course-related permissions.

    Provides access to the course object from dependency kwargs so that
    permission checks can be implemented in subclasses.
    """

    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        """Initialize the base course permission.

        Args:
            request (Request): The current HTTP request.
            **kwargs (PermissionKwargs): Additional keyword arguments
                including the course instance.

        """
        super().__init__(request, **kwargs)
        self.course = kwargs['course']


class BaseAuthorCoursePermission(
    BaseCoursePermission, BaseAuthorPermission, ABC
):
    """Abstract base class for permissions requiring course and author.

    Inherits from BaseCoursePermission and BaseAuthorPermission.
    Useful for checks requiring both author identity and course context.
    """

    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        """Initialize the base author course permission.

        Args:
            request (Request): The current HTTP request.
            **kwargs (PermissionKwargs): Additional keyword arguments
                including the course and author context.

        """
        super().__init__(request, **kwargs)


class IsCourseActive(BaseCoursePermission):
    """Permission that checks whether a course is active."""

    async def validate_permission(self) -> None:
        """Validate that the course is active.

        Raises:
            UserPermissionException: If the course is inactive.

        """
        if self.course.is_active:
            return  # Active courses are accessible to everyone
        raise UserPermissionException


class IsAuthorCourse(BaseAuthorCoursePermission):
    """Permission that checks whether the current author owns the course."""

    async def validate_permission(self) -> None:
        """Validate that the current author is the course's owner.

        Raises:
            UserPermissionException: If the author is not the course owner.

        """
        author = self._is_author_authorized()
        if author.id == self.course.author_id:
            return  # Author can access inactive courses
        raise UserPermissionException
