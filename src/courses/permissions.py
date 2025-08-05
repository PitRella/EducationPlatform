from fastapi.requests import Request

from src.base.permission import BasePermission
from src.courses.models import Course
from src.users import Author
from src.users.exceptions import UserPermissionException


class CourseAuthorPermission(BasePermission):
    def __init__(
        self, request: Request, author: Author | None, course: Course
    ) -> None:
        super().__init__(request=request)
        self.author: Author | None = author
        self.course = course

    async def validate_permission(self) -> None:
        if self.author and self.author.id == self.course.author_id:
            return  # If user an author - can get even inactive course
        if self.course.is_active:
            return  # No admin can only view active courses
        raise UserPermissionException
