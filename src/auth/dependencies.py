from typing import Annotated

from fastapi import Depends
from fastapi.params import Security
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from src.auth.services import AuthService
from src.base.dependencies import get_service
from src.users.exceptions import UserNotAuthorizedException
from src.users.models import User
from src.users.permissions.user import BaseUserPermission
from src.users.services import UserService

oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
    auto_error=False,
)


async def _get_optional_user_from_jwt(
    token: Annotated[str, Security(oauth_scheme)],
    auth_service: Annotated[AuthService, Depends(get_service(AuthService))],
    user_service: Annotated[UserService, Depends(get_service(UserService))],
) -> User | None:
    if not token:
        return None
    user_id = await auth_service.validate_token_for_user(token)
    return await user_service.get_user_by_id(user_id)


class UserPermissionDependency:
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

    def __init__(self, permissions: list[type[BaseUserPermission]]):
        # Store a list of permission class types to be validated later
        self.permissions = permissions

    async def __call__(
        self,
        request: Request,
        user: Annotated[User | None, Depends(_get_optional_user_from_jwt)],
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

        # Just to be sure that the user is authenticated after the permission check.
        if not user:
            raise UserNotAuthorizedException
        return user
