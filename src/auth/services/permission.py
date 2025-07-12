from collections.abc import Sequence
from typing import ClassVar, cast

from src.auth.enums import UserAction
from src.auth.exceptions import PermissionException
from src.users.enums import UserRoles
from src.users.models import User


class PermissionService:
    """Service class for managing user permissions and access control.

    This class provides functionality to validate and enforce permission rules
    between users based on their roles. It implements a hierarchical permission
    system where:
    - Superadmins have the highest level access
    - Admins have elevated access but cannot modify superadmins
    - Regular users have no permissions to modify other users
    """

    ALL_USER_ROLES: ClassVar = list(UserRoles)

    @classmethod
    def _get_highest_role_from_user(cls, target_user: User) -> UserRoles:
        """Return the highest role from a user's assigned roles.

        This method iterates through all possible user roles
        in order of hierarchy
        (from highest to lowest) and returns the first role found in the user's
        role list. If no roles are found, returns the default USER role.

        Args:
            target_user (User): The user whose roles are to be checked.

        Returns:
            UserRoles: The highest role found for
             the user, or UserRoles.USER if none is found.

        """
        for role in cls.ALL_USER_ROLES:
            if role in target_user.roles:
                return cast(UserRoles, role)
        return UserRoles.USER

    @classmethod
    def validate_permission(
        cls,
        target_user: User,
        current_user: User,
        action: UserAction,
    ) -> None:
        """Validate whether the current user permission.

        Args:
            target_user (User): The user being acted upon.
            current_user (User): The user performing the action.
            action (UserAction): The action being performed.

        """
        if current_user.is_user_in_admin_group:  # Admin group permissions
            cls._validate_admin_group_permissions(
                target_user,
                current_user,
                action,
            )
        else:  # Regular user permissions
            cls._validate_user_permissions(
                target_user,
                current_user,
                action,
            )

    @classmethod
    def _get_manageable_roles(
        cls,
        current_user: User,
    ) -> Sequence[str]:
        """Return a sequence of user roles that the current.

        This method determines which roles a user can manage
        based on their highest role.
        Users can only manage roles that are lower in hierarchy
        than their own highest role.

        Args:
            current_user (User): The user whose manageable
            roles are being determined.

        Returns:
            Sequence[str]: A sequence of role names
            that the current user can manage.

        """
        highest_role = cls._get_highest_role_from_user(current_user)
        current_permission_index: int = cls.ALL_USER_ROLES.index(highest_role)
        manageable_roles: Sequence[str] = cls.ALL_USER_ROLES[
            current_permission_index + 1 :
        ]
        return manageable_roles

    @classmethod
    def _validate_admin_group_permissions(
        cls,
        target_user: User,
        current_user: User,
        action: UserAction,
    ) -> None:
        """Validate permissions for users in the admin group.

        This method implements specific permission rules for admin users:
        - Admins cannot delete themselves
        - Admins can only manage users with roles lower than their highest role
        - Superadmins can manage all roles except other superadmins

        Args:
            target_user (User): The user being acted upon
            current_user (User): The admin user performing the action,
            action (UserAction): The action being performed

        Raises:
            PermissionException: If the admin user lacks permission
             for the requested action

        """
        # If user admin or superadmin, he cannot delete himself
        if current_user.id == target_user.id:
            match action:
                case (
                    UserAction.DELETE
                    | UserAction.SET_ADMIN_PRIVILEGE
                    | UserAction.REVOKE_ADMIN_PRIVILEGE
                ):
                    raise PermissionException
                case _:
                    return

        # Only superadmin can give admin privileges
        if not current_user.is_user_superadmin:
            match action:
                case (
                    UserAction.SET_ADMIN_PRIVILEGE
                    | UserAction.REVOKE_ADMIN_PRIVILEGE
                ):
                    raise PermissionException

        manageable_roles = cls._get_manageable_roles(current_user)
        highest_target_user_role: UserRoles = cls._get_highest_role_from_user(
            target_user,
        )
        if highest_target_user_role in manageable_roles:
            return
        raise PermissionException

    @classmethod
    def _validate_user_permissions(
        cls,
        target_user: User,
        current_user: User,
        action: UserAction,
    ) -> None:
        """Validate permissions for regular users (non-admin roles).

        Regular users can only perform actions on their own accounts and cannot
        modify other users' accounts.

        Args:
            target_user (User): The user being acted upon
            current_user (User): The user performing the action,
            action (UserAction): The action being performed.

        Raises:
            PermissionException: If the current user attempts
            to modify another user's account

        """
        if current_user.id == target_user.id:
            match action:
                case (
                    UserAction.SET_ADMIN_PRIVILEGE
                    | UserAction.REVOKE_ADMIN_PRIVILEGE
                ):
                    raise PermissionException
                case _:
                    return
        raise PermissionException
