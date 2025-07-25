import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from src.base.permission import BasePermissionService
from src.users.enums import UserRoles
from src.users.exceptions import (
    UserPermissionException,
    UserNotFoundByIdException
)
from src.users.services import UserService
from src.users import User


class BaseUserPermission(BasePermissionService):
    def __init__(
            self,
            user: User,
            request: Request,
            db: AsyncSession
    ):
        super().__init__(user=user, request=request)
        self.db = db
        self.target_user_id: str = request.path_params.get('user_id', '')

    async def validate_permission(
            self,
    ) -> None:
        user_service = UserService(self.db)
        if not uuid.UUID(self.target_user_id):
            raise UserNotFoundByIdException
        target_user = await user_service.get_user_by_id(self.target_user_id)

        if self.user.roles == UserRoles.SUPERADMIN:
            if target_user.roles == UserRoles.SUPERADMIN:
                raise UserPermissionException
        elif self.user.roles == UserRoles.ADMIN:
            if target_user.roles == UserRoles.ADMIN:
                raise UserPermissionException
        else:
            if target_user.roles == UserRoles.USER and target_user.id != self.user.id:
                raise UserPermissionException
