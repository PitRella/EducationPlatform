from fastapi.requests import Request

from src.base.permission import BasePermissionService
from src.users import User
from src.users.enums import UserRoles
from src.users.exceptions import (
    UserPermissionException,
)


class BaseUserPermission(BasePermissionService):
    """Base permission class for managing user access control.

    Validates permissions between authenticated users and target users for
    user management operations. Enforces role-based access control rules
    to prevent unauthorized modifications between users of similar roles.

    Attributes:
        user (User): The authenticated user making the request
        request (Request): The current HTTP request
        target_user (User): The user being targeted by the operation

    """

    def __init__(
        self,
        user: User,
        request: Request,
        target_user: User,
    ):
        """Initialize BaseUserPermission with an authenticated users.

        Args:
            user (User): The authenticated user making the request
            request (Request): The current HTTP request
            target_user (User): The user being targeted by the operation

        The class manages permissions between authenticated users,
        enforcing role-based access control for user management operations.

        """
        super().__init__(user=user, request=request)
        self.target_user = target_user

    async def validate_permission(
        self,
    ) -> None:
        """Validate permissions between the authenticated users.

        Checks role-based permissions between the authenticated users.
        Raises UserPermissionException if:
        - A superadmin tries to modify another superadmin
        - An admin tries to modify another admin
        - Any other permission validation fails

        Returns:
            None

        Raises:
            UserPermissionException: If permission validation fails

        """
        if (
            self.user.roles == UserRoles.SUPERADMIN
            and self.target_user.roles == UserRoles.SUPERADMIN
        ) or (
            self.user.roles == UserRoles.ADMIN
            and self.target_user.roles == UserRoles.ADMIN
        ):
            raise UserPermissionException
        raise UserPermissionException
