from abc import ABC

from fastapi.requests import Request

from src.base.permission import BasePermission
from src.users import User
from src.users.exceptions import (
    UserPermissionException, UserNotAuthorizedException,
)


# Enforces a contract for permission validation logic.
class BaseUserPermission(BasePermission, ABC):
    """Abstract base class for implementing permission validation.

    Provides a standardized interface for permission checking.
    All permission services must inherit from this class and implement the
    validate_permission() method to enforce their specific access control rules.

    Attributes:
        user (User): The authenticated user making the request
        request (Request): The current HTTP request being processed
    """

    def __init__(
            self,
            user: User | None,
            request: Request,
    ):
        super().__init__(request)
        self.user: User | None = user

    def _is_user_authorized(self) -> User:
        if not self.user:
            raise UserNotAuthorizedException
        return self.user


class AdminPermission(BaseUserPermission):
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
            user: User | None,
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
        auth_user: User = self._is_user_authorized()
        if (
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
    """Permission class that enforces superadmin-level access control.

    Validates that only users with superadmin privileges can perform
    certain operations. Prevents superadmins from modifying other
    superadmin users to maintain security separation.

    Attributes:
        Inherits all attributes from BaseUserPermission:
            user (User): The authenticated user making the request
            request (Request): The current HTTP request
            target_user (User): The user being targeted by the operation

    """

    async def validate_permission(
            self,
    ) -> None:
        """Validate superadmin-level permissions.

        Checks if the authenticated user has superadmin privileges and
        ensures they are not trying to modify another superadmin.

        Returns:
            None

        Raises:
            UserPermissionException: If the user is not a superadmin or
                attempts to modify another superadmin

        """
        auth_user: User = self._is_user_authorized()
        if not auth_user.is_user_superadmin or (
                self.target_user.is_user_superadmin
        ):
            raise UserPermissionException
