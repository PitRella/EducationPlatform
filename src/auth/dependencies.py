from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.params import Security
from fastapi.security import OAuth2PasswordBearer

from src.auth.enums import UserAction
from src.auth.services import AuthService, PermissionService
from src.base.dependencies import get_service
from src.users.dependencies import get_user_from_uuid
from src.users.models import User

oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
)


async def get_user_from_jwt(
    token: Annotated[str, Security(oauth_scheme)],
    service: Annotated[AuthService, Depends(get_service(AuthService))],
) -> User:
    """Return FastAPI dependencies for authentication and validation.

    Includes:
    - OAuth2 password bearer scheme for JWT authentication.
    - Dependency to retrieve an AuthService instance.
    - Async dependency to extract a User from a JWT token.
    - Factory for a permission validation dependency
    """
    return await service.validate_token(token)


def validate_user_permission(
    action: UserAction,
) -> Callable[[User, User], User]:
    """Dependency factory that takes user action from enum.

    Then calls dependencies for get user from query_id and from jwt.
    Then validates permission between the two users.

    :param: action: User action to perform. From UserAction Enum
    :return: Target user object if validation succeeds.
    """

    def user_dependencies(
        source_user: Annotated[User, Depends(get_user_from_jwt)],
        target_user: Annotated[User, Depends(get_user_from_uuid)],
    ) -> User:
        PermissionService.validate_permission(
            target_user=target_user,
            current_user=source_user,
            action=action,
        )
        return target_user

    return user_dependencies
