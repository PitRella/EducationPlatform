from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.auth.services import AuthService
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
