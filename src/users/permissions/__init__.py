from .author import BaseAuthorPermission, IsAuthorPermission
from .user import TargetUserAdminPermission, TargetUserSuperadminPermission

__all__ = [
    'BaseAuthorPermission',
    'IsAuthorPermission',
    'TargetUserAdminPermission',
    'TargetUserSuperadminPermission',
]
