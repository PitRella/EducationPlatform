from enum import StrEnum


class UserRole(StrEnum):
    """Enum class representing user roles in the system.

    Defines a hierarchy of user roles with different permission levels:
    - SUPERADMIN: Highest level with full system access
    - ADMIN: Administrative access with elevated permissions
    - USER: Basic user role with standard permissions
    """

    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    USER = 'user'
