from typing import Annotated

from fastapi import Depends
from fastapi.params import Security
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from src.auth.services import AuthService
from src.base.dependencies import get_service
from src.users.permissions.user import BaseUserPermissionService
from src.users.models import User
from src.users.services import UserService

oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
)


async def get_user_from_jwt(
    token: Annotated[str, Security(oauth_scheme)],
    auth_service: Annotated[AuthService, Depends(get_service(AuthService))],
    user_service: Annotated[UserService, Depends(get_service(UserService))],
) -> User:
    """Return FastAPI dependencies for authentication and validation.

    Includes:
    - OAuth2 password bearer scheme for JWT authentication.
    - Dependency to retrieve an AuthService instance.
    - Async dependency to extract a User from a JWT token.
    - Factory for a permission validation dependency
    """
    user_id = await auth_service.validate_token_for_user(token)
    return await user_service.get_user_by_id(user_id)

async def get_optional_user_from_jwt(
    token: Annotated[str, Security(oauth_scheme)],
    auth_service: Annotated[AuthService, Depends(get_service(AuthService))],
    user_service: Annotated[UserService, Depends(get_service(UserService))],
) -> User | None:
    if not token:
        return None
    user_id = await auth_service.validate_token_for_user(token)
    return await user_service.get_user_by_id(user_id)


class PermissionDependency:
    """Permission dependency for permission validation to FastAPI routes.

    This class provides a FastAPI dependency that enforces permission checks
    by validating a list of permission classes against the current request
    and authenticated user.

    The dependency receives:
    - The HTTP request
    - An authenticated user (from JWT token)

    It validates all specified permissions by instantiating each permission
    and calling its validate_permission() method.
    If any permission check fails, an exception is raised.

    Usage:
        @app.get("/protected")
        async def protected_route(
            user: Annotated[User, Depends(
                PermissionDependency([SomePermission])
            )]
        ):
            return {"message": "Access granted"}
    """

    def __init__(self, permissions: list[type[BaseUserPermissionService]]):
        """Initialize PermissionDependency with a list of permission classes.

        Args:
            permissions (list[type[src.users.permissions.user.BaseUserPermissionService]]): List of permission
                class types that will be validated when the dependency is used.
                Each permission class must inherit from BasePermissionService.

        """
        # Store a list of permission class types to be validated later
        self.permissions = permissions

    async def __call__(
        self,
        request: Request,
        user: Annotated[User, Depends(get_user_from_jwt)],
    ) -> User:
        """Callable used as a FastAPI dependency.

        It receives the request and
        authenticated user, applies all permission classes, and raises
        if any permission fails.
        """
        for permission_cls in self.permissions:
            # Instantiate permission with request and user
            p_class = permission_cls(request=request, user=user)
            #  the actual permission check
            await p_class.validate_permission()

        # If all checks pass, return the user
        return user
