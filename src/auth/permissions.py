from src.base.permission import BasePermissionService


class IsAuthenticated(BasePermissionService):
    async def validate_permission(
            self,
    ) -> None:
        """
        Explicitly indicates that the user must be authenticated;

        Actual check is handled in the base class.
        """
