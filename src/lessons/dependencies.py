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
    def __init__(
        self,
        permissions: Sequence[type[BaseLessonPermission]],
        logic: Literal['AND', 'OR'] = BasePermissionDependency._LOGIC_AND,
    ):
        super().__init__(permissions, logic)

    async def __call__(
        self,
        request: Request,
        author: Annotated[
            Author | None, Depends(_get_optional_author_from_jwt)
        ],
        lesson: Annotated[Lesson, Depends(_get_lesson_by_id)],
    ) -> Lesson:
        await self._validate_permissions(
            request=request,
            lesson=lesson,
            author=author,
        )
        return lesson
