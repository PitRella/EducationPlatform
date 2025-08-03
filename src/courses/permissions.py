from fastapi.requests import Request

from src.base.permission import BasePermissionService
from src.courses.models import Course
from src.users import User
from src.users.exceptions import UserPermissionException


class CoursePermission(BasePermissionService):
    def __init__(self, request: Request, user: User, course: Course) -> None:
        super().__init__(user=user, request=request)
        self.course = course

    async def validate_permission(self) -> None:
        if self.course.author_id == self.user.id:
            return  # If user an author - can get even inactive course
        if self.course in self.user.purchased_courses:
            return  # User can only check bought courses, even if they are free
        raise UserPermissionException
