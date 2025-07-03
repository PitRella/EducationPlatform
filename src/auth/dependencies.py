from typing import Callable, Annotated

from fastapi import Depends
from fastapi.params import Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.enums import UserAction
from src.users.dependencies import get_user_from_uuid
from src.users.models import User
from src.auth.services import AuthService, PermissionService
from src.database import get_db

oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    """Dependency for retrieving the UserService instance."""
    return AuthService(db_session=db)


async def get_user_from_jwt(
    token: Annotated[str, Security(oauth_scheme)],
    service: Annotated[AuthService, Depends(get_service)],
) -> User:
    """
    Provides FastAPI dependencies for authentication and permission validation.

    Includes:
    - OAuth2 password bearer scheme for JWT authentication.
    - Dependency to retrieve an AuthService instance.
    - Async dependency to extract a User from a JWT token.
    - Factory for a permission validation dependency that checks if the current user can perform a specified action on a target user.
    """
    return await service.validate_token(token)


def validate_user_permission(
    action: UserAction,
) -> Callable[[User, User], User]:
    """
    Dependency factory that takes user action from enum.
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
