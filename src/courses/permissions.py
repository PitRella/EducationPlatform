from abc import ABC

from fastapi.requests import Request

from src.base.permission import BasePermission
from src.courses.models import Course
from src.users import Author
from src.users.exceptions import UserPermissionException


class BaseCoursePermission(BasePermission, ABC):
    def __init__(
            self,
            request: Request,
            author: Author | None,
            course: Course
    ) -> None:
        super().__init__(request=request)
        self.course = course
        self.author: Author | None = author

    def _is_author_authorized(self) -> Author:
        if not self.author:
            raise UserPermissionException
        return self.author


class IsCourseAuthorOrActiveCourse(BaseCoursePermission):
    async def validate_permission(self) -> None:
        if self.course.is_active:
            return  # If the course is active - everyone can get it
        author = self._is_author_authorized()
        if author.id == self.course.author_id:
            return  # If user an author - can get even inactive course
        raise UserPermissionException


class IsCourseActive(BaseCoursePermission):
    async def validate_permission(self) -> None:
        if not self.course.is_active:
            return  # If the course is active - everyone can get it

class IsAuthorCourse(BaseCoursePermission):
    async def validate_permission(self) -> None:
        author = self._is_author_authorized()
        if author.id == self.course.author_id:
            return  # If user an author - can get even inactive course
        raise UserPermissionException