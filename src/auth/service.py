import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import Token
from src.auth.dal import AuthDAL
from src.users.dal import UserDAL
from src.hashing import Hasher
from src.settings import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer
from src.settings import REFRESH_TOKEN_EXPIRE_DAYS
from jose import jwt
from src.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/token')


class AuthService:
    @classmethod
    async def auth_user(
            cls,
            email: str,
            password: str,
            db: AsyncSession
    ) -> Optional[User]:
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_email(email)
        if not user or not Hasher.verify_password(password, user.password):
            return None
        return user

    @classmethod
    async def create_token(
            cls,
            user_id: uuid.UUID,
            db: AsyncSession
    ) -> Token:
        """
        Create a pair of tokens for user

        :param user_id: An id of user that want to create tokens
        :param db: Database async session
        :return: Token: A Pair of refresh and access tokens with their type
        """
        access_token: str = await cls._generate_access_token(
            user_id=user_id
        )
        refresh_token, tm_delta = await (
            cls._generate_refresh_token_timedelta())
        async with db as session:
            async with session.begin():
                auth_dal = AuthDAL(session)
                await auth_dal.create_token(
                    user_id,
                    refresh_token,
                    tm_delta.total_seconds()
                )
        return Token(access_token=access_token, refresh_token=refresh_token)

    @classmethod
    async def _generate_access_token(
            cls,
            user_id: uuid.UUID
    ) -> str:
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.now() + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        encoded_jwt = jwt.encode(
            to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return f'Bearer {encoded_jwt}'

    @classmethod
    async def _generate_refresh_token_timedelta(cls) -> Tuple[
        uuid.UUID, timedelta]:
        """Generate refresh token and timedelta"""
        return uuid.uuid4(), timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
