from abc import ABC
from typing import Unpack

from fastapi.requests import Request
from src.base.permission import BasePermission, PermissionKwargs
from src.lessons.exceptions import LessonIsNotPublishedException
from src.users.permissions import BaseAuthorPermission


class BaseLessonPermission(BasePermission, ABC):
    def __init__(
            self,
            request: Request,
            **kwargs: Unpack[PermissionKwargs],
    ):
        super().__init__(request, **kwargs)
        self.lesson = kwargs['lesson']

class BaseAuthorLessonPermission(
    BaseLessonPermission,
    BaseAuthorPermission,
    ABC
):
    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        super().__init__(request, **kwargs)

class IsLessonPublished(BaseLessonPermission):
    async def validate_permission(self) -> None:
        if self.lesson.is_published:
            return None # If the lesson published - everyone can get it
        raise LessonIsNotPublishedException

class IsLessonAuthor(BaseAuthorLessonPermission):
    async def validate_permission(
        self,
    ) -> None:
        author = self._is_author_authorized()
        if self.lesson.course.author_id == author.id:
            return None # If user an author - can get an even inactive lesson
        raise LessonIsNotPublishedException