from typing import Callable

from fastapi import Depends
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


def get_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency for retrieving the UserService instance."""
    return AuthService(db_session=db)


async def get_user_from_jwt(
    token: str = Depends(oauth_scheme),
    service: AuthService = Depends(get_service),
) -> User:
    user: User = await service.validate_token(token)
    return user


def validate_user_permission(
    action: UserAction,
) -> Callable[[User, User], None]:  # исправлено
    def user_dependencies(
        source_user: User = Depends(get_user_from_jwt),
        target_user: User = Depends(get_user_from_uuid),
    ) -> None:
        PermissionService.validate_permission(
            target_user=target_user,
            current_user=source_user,
            action=action,
        )

    return user_dependencies
