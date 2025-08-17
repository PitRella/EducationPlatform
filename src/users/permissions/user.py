from abc import ABC
from typing import Unpack

from fastapi.requests import Request

from src.base.permission import BasePermission, PermissionKwargs
from src.users import User
from src.users.exceptions import (
    UserNotAuthorizedException,
    UserPermissionException,
)


# Enforces a contract for permission validation logic.
class BaseUserPermission(BasePermission, ABC):
    def __init__(
            self,
            request: Request,
            **kwargs: Unpack[PermissionKwargs],
    ):
        super().__init__(request, **kwargs)
        self.user: User | None = kwargs.get('user')

    def _is_user_authorized(self) -> User:
        if not self.user:
            raise UserNotAuthorizedException
        return self.user


class AdminPermission(BaseUserPermission):
    def __init__(
            self,
            request: Request,
            **kwargs: Unpack[PermissionKwargs],
    ):
        super().__init__(request, **kwargs)
        self.target_user = kwargs['target_user']

    async def validate_permission(
            self,
    ) -> None:
        auth_user: User = self._is_user_authorized()
        if (
                not auth_user.is_user_admin
                or
                (  # Superadmin cannot interact with another superadmin
                        auth_user.is_user_superadmin
                        and self.target_user.is_user_superadmin
                )
                or (  # Admin cannot interact with another admin
                auth_user.is_user_admin and self.target_user.is_user_admin
        )
                or (  # Admin cannot interact with superadmin
                auth_user.is_user_admin and self.target_user.is_user_superadmin
        )
        ):
            raise UserPermissionException


class SuperadminPermission(AdminPermission):
    async def validate_permission(
            self,
    ) -> None:
        auth_user: User = self._is_user_authorized()
        if not auth_user.is_user_superadmin or (
                self.target_user.is_user_superadmin
        ):
            raise UserPermissionException
