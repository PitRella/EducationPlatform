from abc import ABC
from typing import Unpack

from fastapi.requests import Request

from src.base.permission import BasePermission, PermissionKwargs
from src.users import User
from src.users.exceptions import (
    UserNotAuthorizedException,
    UserPermissionException,
)


class BaseUserPermission(BasePermission, ABC):
    """Abstract base class for user-related permissions.

    Provides access to the user object from dependency kwargs and a method
    to check if the user is authorized.
    """

    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        """Initialize the base user permission.

        Args:
            request (Request): The current HTTP request.
            **kwargs (PermissionKwargs): Additional keyword arguments,
                including the 'user'.

        """
        super().__init__(request, **kwargs)
        self.user: User | None = kwargs.get('user')

    def _is_user_authorized(self) -> User:
        """Check if a user is authorized.

        Raises:
            UserNotAuthorizedException: If the user is not provided.

        Returns:
            User: The authenticated user.

        """
        if not self.user:
            raise UserNotAuthorizedException
        return self.user


class TargetUserAdminPermission(BaseUserPermission):
    """Permission class to validate admin access on a target user.

    Ensures that only admins can perform certain operations and prevents
    interactions with other admins or superadmins depending on the role.
    """

    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        """Initialize permission with target user.

        Args:
            request (Request): The current HTTP request.
            **kwargs (PermissionKwargs): Must include 'target_user'.

        """
        super().__init__(request, **kwargs)
        self.target_user = kwargs['target_user']

    async def validate_permission(self) -> None:
        """Validate if the current user has admin permissions for the target.

        Raises:
            UserPermissionException: If the user does not have permission.

        """
        auth_user: User = self._is_user_authorized()
        if (
            not auth_user.is_user_admin
            or (
                auth_user.is_user_superadmin
                and self.target_user.is_user_superadmin
            )
            or (auth_user.is_user_admin and self.target_user.is_user_admin)
            or (auth_user.is_user_admin and self.target_user.is_user_superadmin)
        ):
            raise UserPermissionException


class TargetUserSuperadminPermission(TargetUserAdminPermission):
    """Permission class to validate superadmin access on a target user.

    Ensures that only superadmins can perform operations and prevents
    interactions with other superadmins.
    """

    async def validate_permission(self) -> None:
        """Validate if the current user has superadmin permissions.

        Raises:
            UserPermissionException: If the user does not have permission.

        """
        auth_user: User = self._is_user_authorized()
        if (
            not auth_user.is_user_superadmin
            or self.target_user.is_user_superadmin
        ):
            raise UserPermissionException
