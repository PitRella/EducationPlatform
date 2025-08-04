from src.users.permissions.user import BaseUserPermission


class IsAuthenticated(BaseUserPermission):
    async def validate_permission(
        self,
    ) -> None:
        self._is_user_authorized()
