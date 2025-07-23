from typing import Annotated

from fastapi import Depends
from fastapi.params import Security
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from src.auth.services import AuthService
from src.base.dependencies import get_service
from src.base.permission import BasePermissionService
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

# Dependency that applies a list of permission classes to a route.
# Each permission is initialized, and its validate_permission() is called.
class PermissionDependency:
    def __init__(self, permissions: list[type[BasePermissionService]]):
        # Store a list of permission class types to be validated later
        self.permissions = permissions

    async def __call__(
            self,
            request: Request,
            user: Annotated[User, Depends(get_user_from_jwt)],
    ) -> User:
        """Callable used as a FastAPI dependency. It receives the request and
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
