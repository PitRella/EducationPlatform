from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.session import get_db
from src.users.models import User
from src.auth.services import AuthService

oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


async def get_user_from_jwt(
        token: str = Depends(oauth_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency that extracts and validates a user from a JWT token.

    Args:
        token (str): JWT access token obtained from OAuth2 scheme.
        db (AsyncSession): Async database session for database operations.

    Returns:
        User: Authenticated user object if token is valid.

    Raises:
        WrongCredentialsException: If token is invalid.
        AccessTokenExpiredException: If token has expired.
    """

    user: User = await AuthService.validate_token(token, db)
    return user
