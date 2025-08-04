from src.users.permissions.user import BaseUserPermissionService


class IsAuthenticated(BaseUserPermissionService):
    """Permission class that ensures a user is authenticated.

    This permission class validates that a request has a properly authenticated
    user. It is used to protect endpoints that require user authentication
    without any additional role or permission checks.

    The actual authentication validation is handled by the parent
    BasePermissionService class through user dependency injection.

    Examples:
        @app.get("/protected")
        async def protected_endpoint(
            user: Annotated[User, Depends(
                PermissionDependency([IsAuthenticated])
            )]
        ):
            return {"message": "Access granted"}

    """

    async def validate_permission(
        self,
    ) -> None:
        """Validate that the user is authenticated for the current request.

        This permission class ensures that a valid authenticated user exists
        for protected endpoints. The actual authentication validation is
        handled by the parent BasePermissionService class through the user
        dependency injection.

        Returns:
            None

        Raises:
            HTTPException: If a user is not properly authenticated, an exception
                will be raised by the authentication dependencies.

        """
