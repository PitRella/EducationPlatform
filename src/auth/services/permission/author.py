from src.auth.enums.courses import AuthorAction
from src.base.permission import BasePermissionService
from src.users import User
from src.users.models import Author


class AuthorPermissionService(BasePermissionService[Author, AuthorAction]):
    """Service class for managing author permissions and access control."""

    def validate_permission(
            cls, target_model: Author, current_user: User, action: AuthorAction
    ) -> None:
        if current_user.is_user_in_admin_group:
            pass
