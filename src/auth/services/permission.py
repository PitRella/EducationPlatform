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

    @classmethod
    def validate_permission(
        cls, target_user: User, current_user: User, action: UserAction
    ) -> None:
        match current_user.roles:
            case UserRoles.SUPERADMIN:
                cls._validate_superadmin_permissions(
                    target_user, current_user, action
                )
            case UserRoles.ADMIN:
                cls._validate_admin_permissions(
                    target_user, current_user, action
                )
            case UserRoles.USER:
                cls._validate_user_permissions(
                    target_user, current_user, action
                )

    @staticmethod
    def _validate_superadmin_permissions(
        target_user: User, current_user: User, action: UserAction
    ) -> None:
        if current_user == target_user:
            match action:
                case UserAction.DELETE:  # Superadmin cannot delete himself
                    raise PermissionException
                case _:
                    return
        else:
            match target_user.roles:
                # Superadmin cannot perform actions on another superadmin
                case UserRoles.SUPERADMIN:
                    raise PermissionException

    @staticmethod
    def _validate_admin_permissions(
        target_user: User, current_user: User, action: UserAction
    ) -> None:
        if current_user == target_user:
            match action:
                case UserAction.DELETE:  # Admin cannot delete himself
                    raise PermissionException
                case _:
                    return
        else:
            match target_user.roles:
                # Admin cannot perform actions on another superadmin or admin
                case UserRoles.SUPERADMIN, UserRoles.ADMIN:
                    raise PermissionException

    @staticmethod
    def _validate_user_permissions(
        target_user: User, current_user: User, action: UserAction
    ) -> None:
        match target_user.roles:
            # User cannot perform actions on another superadmin, admin or user
            case UserRoles.SUPERADMIN, UserRoles.ADMIN, UserRoles.USER:
                raise PermissionException
