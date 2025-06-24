from enum import StrEnum


class UserRoles(StrEnum):
    """Enum class representing user roles in the system.

    Defines a hierarchy of user roles with different permission levels:
    - SUPERADMIN: Highest level with full system access
    - ADMIN: Administrative access with elevated permissions
    - USER: Basic user role with standard permissions
    """

    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"

    @classmethod
    def admin_roles(cls) -> list["UserRoles"]:
        """Returns a list of admin-level roles in the system.

        This method provides a list of roles that are considered administrative,
        including both SUPERADMIN and ADMIN roles.

        Returns:
            list[UserRoles]: List containing admin-level role enums
        """

        return [cls.SUPERADMIN, cls.ADMIN]

    @classmethod
    def is_admin(cls, role: "UserRoles") -> bool:
        """Check if a given role has administrative privileges.

        Args:
            role (UserRoles): The role to check for admin status

        Returns:
            bool: True if the role is either SUPERADMIN or ADMIN, False otherwise

        This method determines if a given user role has administrative privileges
        by checking if it's included in the admin_roles list.
        """

        return role in cls.admin_roles()
