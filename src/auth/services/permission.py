from src.auth.exceptions import PermissionException
from src.users.models import User
from src.users.enums import UserRoles


class PermissionService:
    """Service class for managing user permissions and access control.

    This class provides functionality to validate and enforce permission rules
    between users based on their roles. It implements a hierarchical permission
    system where:
    - Superadmins have the highest level access
    - Admins have elevated access but cannot modify superadmins
    - Regular users have no permissions to modify other users
    """

    @classmethod
    def validate_permission(
        cls,
        target_user: User,
        current_user: User,
    ) -> None:
        """Validate if the current user has permission to perform actions on the target user.

        Permission rules:
        - Superadmin can perform actions on any user except other superadmins
        - Admin can perform actions on any user except admins and superadmins
        - Regular users have no permissions to perform actions on other users

        Args:
            target_user: User object on which action is being performed
            current_user: User object requesting to perform the action

        Raises:
            PermissionException: If the current user doesn't have required permissions
        """
        # Every user can get info about himself
        # if target_user.user_id == current_user.user_id:
        #     return
        if target_user == current_user:
            return
        # Superadmin can do anything for every user except other superadmin
        elif (
            UserRoles.SUPERADMIN in current_user.roles
            and UserRoles.SUPERADMIN not in target_user.roles
        ):
            return
        # Admin can do anything for every user except other admin and superadmin
        elif (
            UserRoles.ADMIN in current_user.roles
            and UserRoles.SUPERADMIN not in target_user.roles
            and UserRoles.ADMIN not in target_user.roles
        ):
            return
        # Regular user can do nothing for other users except superadmin and admin
        elif (
            UserRoles.USER in target_user.roles and target_user == current_user
        ):
            return
        raise PermissionException
