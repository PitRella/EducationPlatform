from fastapi.requests import Request

from src.base.permission import BaseOptionalPermissionService
from src.courses.models import Course
from src.users import User
from src.users.exceptions import UserPermissionException


class CoursePermission(BaseOptionalPermissionService):
    def __init__(
            self,
            request: Request,
            user: User | None,
            course: Course
    ) -> None:
        super().__init__(user=user, request=request)
        self.course = course

    async def validate_permission(self) -> None:
        if self.user and self.user.id == self.course.author_id:
            return  # If user an author - can get even inactive course
        if self.course.is_active:
            return  # No admin can only view active courses
        raise UserPermissionException
