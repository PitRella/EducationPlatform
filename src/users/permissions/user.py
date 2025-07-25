from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from src.base.permission import BasePermissionService
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

    async def validate_permission(
            self,
    ) -> None:
        pass

