from typing import Sequence

from src.auth.exceptions import PermissionException
from src.users.models import User
from src.users.enums import UserRoles
from src.auth.enums import UserAction


class PermissionService:
    """Service class for managing user permissions and access control.

    This class provides functionality to validate and enforce permission rules
    between users based on their roles. It implements a hierarchical permission
    system where:
    - Superadmins have the highest level access
    - Admins have elevated access but cannot modify superadmins
    - Regular users have no permissions to modify other users
    """

    ALL_USER_ROLES = list(UserRoles)

    @classmethod
    def _get_highest_role_from_user(cls, target_user: User) -> UserRoles:
        for role in cls.ALL_USER_ROLES:
            if role in target_user.roles:
                return role
        return UserRoles.USER

    @classmethod
    def validate_permission(
        cls, target_user: User, current_user: User, action: UserAction
    ) -> None:
        """validates if the current user has permission to perform a given action on the target user.

        Args:
            target_user (User): The user being acted upon.
            current_user (User): The user performing the action.
            action (UserAction): The action being performed.
        """
        match current_user.roles:
            case UserRoles.SUPERADMIN | UserRoles.ADMIN:
                cls._validate_admin_group_permissions(
                    target_user, current_user, action
                )
            case UserRoles.USER:
                cls._validate_user_permissions(
                    target_user, current_user, action
                )

    @classmethod
    def _get_manageable_roles(
        cls,
        current_user: User,
    ) -> Sequence[str]:
        highest_role = cls._get_highest_role_from_user(current_user)
        current_permission_index: int = cls.ALL_USER_ROLES.index(highest_role)
        manageable_roles: Sequence[str] = cls.ALL_USER_ROLES[
            current_permission_index + 1 :
        ]
        return manageable_roles

    @classmethod
    def _validate_admin_group_permissions(
        cls, target_user: User, current_user: User, action: UserAction
    ) -> None:
        # If user admin or superadmin, he cannot delete himself
        if current_user.user_id == target_user.user_id:
            match action:
                case UserAction.DELETE:
                    raise PermissionException
                case _:
                    return
        manageable_roles = cls._get_manageable_roles(current_user)
        if any(role in manageable_roles for role in target_user.roles):
            return
        raise PermissionException
