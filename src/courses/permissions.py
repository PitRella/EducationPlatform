from src.base.permission import BasePermissionService
from src.users.exceptions import UserPermissionException


class CoursePermission(BasePermissionService):
    def __init__(self, user, request, course):
        super().__init__(user=user, request=request)
        self.course = course
        

    async def validate_permission(self) -> None:
        if self.course.author_id == self.user.id:
            return # If user an author - can get even inactive course
        elif self.course in self.user.purchased_courses:
            return # User can only check bought courses, even if they are free
        raise UserPermissionException
