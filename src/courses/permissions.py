from abc import ABC
from typing import Unpack

from fastapi.requests import Request

from src.base.permission import BasePermission, PermissionKwargs
from src.users.exceptions import UserPermissionException
from src.users.permissions import BaseAuthorPermission


class BaseCoursePermission(BasePermission, ABC):
    def __init__(
            self,
            request: Request,
            **kwargs: Unpack[PermissionKwargs],
    ):
        super().__init__(request, **kwargs)
        self.course = kwargs['course']


class BaseAuthorCoursePermission(
    BaseCoursePermission,
    BaseAuthorPermission,
    ABC
):
    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        super().__init__(request, **kwargs)


class IsCourseActive(BaseCoursePermission):
    async def validate_permission(self) -> None:
        if not self.course.is_active:
            return  # If the course is active - everyone can get it


class IsAuthorCourse(BaseAuthorCoursePermission):
    async def validate_permission(self) -> None:
        author = self._is_author_authorized()
        if author.id == self.course.author_id:
            return  # If user an author - can get even inactive course
        raise UserPermissionException
