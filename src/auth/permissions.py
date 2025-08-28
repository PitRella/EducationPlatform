from src.users.permissions.user import BaseUserPermission


class IsAuthenticated(BaseUserPermission):
    """Permission class that ensures the user is authenticated.

    This class checks whether the user is present in the request context.
    If the user is not authenticated, a `UserNotAuthorizedException` is raised.
    """

    async def validate_permission(self) -> None:
        """Validate that the current user is authenticated.

        Raises:
            UserNotAuthorizedException: If no user is present in the request.

        """
        self._is_user_authorized()
