from abc import ABC
from typing import Unpack

from fastapi.requests import Request
from src.base.permission import BasePermission, PermissionKwargs
from src.lessons.exceptions import LessonIsNotPublishedException


class BaseLessonPermission(BasePermission, ABC):
    def __init__(
            self,
            request: Request,
            **kwargs: Unpack[PermissionKwargs],
    ):
        super().__init__(request, **kwargs)
        self.lesson = kwargs['lesson']

class IsLessonPublished(BaseLessonPermission):
    async def validate_permission(self) -> None:
        if not self.lesson.is_published:
            raise LessonIsNotPublishedException