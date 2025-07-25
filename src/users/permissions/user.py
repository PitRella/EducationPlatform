from fastapi.requests import Request
from src.base.permission import BasePermissionService
from src.users.enums import UserRoles
from src.users.exceptions import (
    UserPermissionException,
)
from src.users import User


class BaseUserPermission(BasePermissionService):
    def __init__(
            self,
            user: User,
            request: Request,
            target_user: User,
    ):
        super().__init__(user=user, request=request)
        self.target_user = target_user


    async def validate_permission(
            self,
    ) -> None:
        if self.user.roles == UserRoles.SUPERADMIN:
            if self.target_user.roles == UserRoles.SUPERADMIN:
                raise UserPermissionException
        elif self.user.roles == UserRoles.ADMIN:
            if self.target_user.roles == UserRoles.ADMIN:
                raise UserPermissionException
        raise UserPermissionException