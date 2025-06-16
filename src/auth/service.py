import uuid
from calendar import timegm
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Union, Any, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    WrongCredentialsException,
    AccessTokenExpiredException, RefreshTokenException
)
from src.auth.models import RefreshSessionModel
from src.auth.schemas import Token
from src.auth.dal import AuthDAL
from src.users.dal import UserDAL
from src.hashing import Hasher
from src.settings import (
    ALGORITHM,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.settings import REFRESH_TOKEN_EXPIRE_DAYS
from jose import jwt, JWTError
from src.users.models import User


class AuthService:
    @classmethod
    async def auth_user(
            cls,
            email: str,
            password: str,
            db: AsyncSession
    ) -> User:
        """
        Method to find user based on email and pass
        :param email: User email
        :param password: User unhashed password
        :param db: AsyncSession
        :return: Optional[User]
        """
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_email(email)
        if not user or not Hasher.verify_password(password, user.password):
            raise WrongCredentialsException
        return user

    @classmethod
    async def validate_token(
            cls,
            user_jwt_token: str,
            db: AsyncSession
    ) -> User:
        """
        Method to validate token and take user if token is valid
        :param user_jwt_token: JWT token
        :param db: Async session to db.
        :return: User or None
        """
        decoded_jwt: dict[str, str | int] = await cls._eject_token(
            user_jwt_token)
        cls._validate_access_token_expire(decoded_jwt)
        user_id: Optional[int | str] = decoded_jwt.get("sub", None)
        if not user_id or isinstance(user_id, int):
            raise WrongCredentialsException
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_id(user_id)
        if not user:
            raise WrongCredentialsException
        return user

    @classmethod
    def _validate_access_token_expire(
            cls,
            decoded_jwt: dict[str, str | int]
    ) -> None:
        """
        Method to validate access token expiration date
        :param decoded_jwt: Decoded jwt object
        :return: None
        """
        jwt_exp_date: int = int(decoded_jwt.get("exp", 0))
        current_time: int = timegm(datetime.now().utctimetuple())
        if not jwt_exp_date or current_time >= jwt_exp_date:
            raise AccessTokenExpiredException

    @classmethod
    async def _validate_refresh_token_expire(
            cls,
            refresh_token_model: RefreshSessionModel,
            db: AsyncSession,
    ) -> None:
        if (datetime.now(timezone.utc) >= refresh_token_model.created_at
                + timedelta(seconds=refresh_token_model.expires_in)):
            async with db as session:
                async with session.begin():
                    auth_dal: AuthDAL = AuthDAL(session)
                    await auth_dal.delete_refresh_token(
                        refresh_token_id=refresh_token_model.id)
            raise RefreshTokenException

    @classmethod
    async def _eject_token(
            cls,
            user_jwt_token: str
    ) -> dict[str, str | int]:
        """
        Function to eject token and return decoded jwt.
        :param user_jwt_token: User access token.
        :return: Decoded jwt.
        """
        try:
            decoded_jwt: dict[str, str | int] = jwt.decode(
                token=user_jwt_token,
                key=SECRET_KEY,
                algorithms=ALGORITHM
            )
        except JWTError:
            raise WrongCredentialsException
        return decoded_jwt

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
        access_token: str = cls._generate_access_token(
            user_id=user_id
        )
        refresh_token, tm_delta = cls._generate_refresh_token_timedelta()
        async with db as session:
            async with session.begin():
                auth_dal = AuthDAL(session)
                await auth_dal.create_token(
                    user_id,
                    refresh_token,
                    tm_delta.total_seconds()
                )
        return Token(
            access_token=access_token,
            refresh_token=str(refresh_token)
        )

    @classmethod
    async def refresh_token(
            cls,
            refresh_token: uuid.UUID,
            db: AsyncSession
    ) -> Token:
        async with db as session:
            async with session.begin():
                auth_dal: AuthDAL = AuthDAL(db_session=db)
                user_dal: UserDAL = UserDAL(db_session=db)
                refresh_token_model: Optional[
                    RefreshSessionModel] = await auth_dal.get_refresh_token(
                    refresh_token=refresh_token
                )
                if not refresh_token_model:
                    raise RefreshTokenException
                await cls._validate_refresh_token_expire(
                    refresh_token_model=refresh_token_model,
                    db=db
                )
                user_id: uuid.UUID = refresh_token_model.user_id
                user: Optional[User] = await user_dal.get_user_by_id(
                    user_id=user_id)
                if not user:
                    raise RefreshTokenException
                access_token: str = cls._generate_access_token(user_id=user_id)
                updated_refresh_token, tm_delta = cls._generate_refresh_token_timedelta()
                updated_refresh_token_model: Optional[
                    RefreshSessionModel] = await auth_dal.update_refresh_token(
                    refresh_token_id=refresh_token_model.id,
                    refresh_token=updated_refresh_token,
                    expires_at=tm_delta.total_seconds(),
                )
                if not updated_refresh_token_model:
                    raise RefreshTokenException
                return Token(
                    access_token=access_token,
                    refresh_token=str(updated_refresh_token)
                )

    @classmethod
    def _generate_access_token(
            cls,
            user_id: uuid.UUID
    ) -> str:
        """
        Generate a new access token
        :param user_id: UUID of user
        :return: access token
        """
        to_encode: dict[str, str | datetime] = {
            "sub": str(user_id),
            "exp": datetime.now() + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        encoded_jwt: str = jwt.encode(
            to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return f'Bearer {encoded_jwt}'

    @classmethod
    def _generate_refresh_token_timedelta(cls) -> Tuple[
        uuid.UUID, timedelta]:
        """
        Generate refresh token and timedelta
        :return: refresh token and timedelta
        """
        return uuid.uuid4(), timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
