from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.params import Security
from fastapi.security import OAuth2PasswordBearer

from src.auth.enums import UserAction
from src.auth.services import AuthService, UserPermissionService
from src.base.dependencies import get_service
from src.users.dependencies import get_user_from_uuid
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
        UserPermissionService.validate_permission(
            target_model=target_user,
            current_user=source_user,
            action=action,
        )
        return target_user

    return user_dependencies
