from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import AuthService
from src.session import get_db
from src.users.models import User

oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

async def get_user_from_jwt(
        token=Depends(oauth_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    Method to take user_id from access token.
    :param token: Access token.
    :param db: Async session to db.
    :return: User.
    """
    user: User = await AuthService.validate_token(token, db)
    return user
