import uuid
from typing import Optional, Union, cast

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dal import AuthDAL
from src.auth.exceptions import (
    WrongCredentialsException,
    RefreshTokenException
)
from src.auth.models import RefreshSessionModel
from src.auth.schemas import Token
from src.auth.services.token_manager import TokenManager
from src.hashing import Hasher
from src.users.dal import UserDAL
from src.users.models import User


class AuthService:
    @staticmethod
    def _verify_user_password(user: Optional[User], password: str) -> None:
        """
        Verify if the provided password matches the user's stored password hash.

        Args:
            user: User model instance containing the stored password hash
            password: Plain text password to verify

        Raises:
            WrongCredentialsException: If user is None or password verification fails
        """
        if not user or not Hasher.verify_password(
                password,
                user.password
        ):
            raise WrongCredentialsException

    @classmethod
    async def auth_user(
            cls,
            email: str,
            password: str,
            db: AsyncSession
    ) -> User:
        """
        Authenticate a user using email and password.

        Args:
            email: User's email address
            password: User's password in plain text
            db: AsyncSession instance for database operations

        Returns:
            User: Authenticated user model instance

        Raises:
            WrongCredentialsException: If a user is not found or password verification fails
        """
        async with db as session:
            async with session.begin():
                user_dal: UserDAL = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_email(email)
        cls._verify_user_password(user, password)
        return cast(User, user)

    @staticmethod
    def _get_user_id_from_jwt(decoded_jwt: dict[str, str | int]) -> str:
        """
        Extract and validate user ID from a decoded JWT token.

        Args:
            decoded_jwt: Dictionary containing decoded JWT claims

        Returns:
            str: The validated user ID from the token

        Raises:
            WrongCredentialsException: If user ID is missing or has an invalid type
        """
        user_id: Optional[int | str] = decoded_jwt.get("sub", None)
        if not user_id or isinstance(user_id, int):
            raise WrongCredentialsException
        return user_id

    @classmethod
    async def validate_token(
            cls,
            user_jwt_token: str,
            db: AsyncSession
    ) -> User:
        """
        Validate a JWT token and return the associated user.

        Args:
            user_jwt_token: JWT token string to validate
            db: AsyncSession instance for database operations

        Returns:
            User: User model instance associated with the token

        Raises:
            WrongCredentialsException: If the token is invalid, or the user has not found
            AccessTokenExpiredException: If token has expired
        """

        decoded_jwt: dict[str, str | int] = TokenManager.decode_access_token(
            token=user_jwt_token)
        TokenManager.validate_access_token_expired(decoded_jwt)
        user_id: Union[uuid.UUID, str] = cls._get_user_id_from_jwt(decoded_jwt)
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_id(user_id)
        if not user:
            raise WrongCredentialsException
        return user

    @classmethod
    async def create_token(
            cls,
            user_id: uuid.UUID,
            db: AsyncSession
    ) -> Token:
        """
        Create a new token pair (access token and refresh token) for a user.

        Args:
            user_id: UUID of the user to create tokens for
            db: AsyncSession instance for database operations

        Returns:
            Token: Token schema instance containing access_token and refresh_token

        Note:
            The refresh token is stored in the database with its expiration time
        """

        access_token: str = TokenManager.generate_access_token(
            user_id=user_id
        )
        refresh_token, tm_delta = TokenManager.generate_refresh_token()
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
        """
        Refresh an existing token pair using a refresh token.

        Args:
            refresh_token: UUID of the refresh token to validate and update
            db: AsyncSession instance for database operations

        Returns:
            Token: New token pair containing fresh access_token and refresh_token

        Raises:
            RefreshTokenException: If the refresh token is invalid, expired, or the user is not found
        """

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
                TokenManager.validate_refresh_token_expired(
                    refresh_token_model=refresh_token_model,
                )
                user_id: uuid.UUID = refresh_token_model.user_id
                user: Optional[User] = await user_dal.get_user_by_id(
                    user_id=user_id)
                if not user:
                    raise RefreshTokenException
                access_token: str = TokenManager.generate_access_token(
                    user_id=user_id)
                updated_refresh_token, tm_delta = TokenManager.generate_refresh_token()
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
    async def logout_user(
            cls,
            refresh_token: uuid.UUID,
            db: AsyncSession
    ) -> None:
        """
        Log out a user by invalidating their refresh token.

        Args:
            refresh_token: UUID of the refresh token to invalidate
            db: AsyncSession instance for database operations

        Raises:
            RefreshTokenException: If the refresh token is not found
        """

        async with db as session:
            async with session.begin():
                auth_dal: AuthDAL = AuthDAL(db_session=db)
                refresh_token_model: Optional[
                    RefreshSessionModel] = await auth_dal.get_refresh_token(
                    refresh_token=refresh_token
                )
                if not refresh_token_model:
                    raise RefreshTokenException
                await auth_dal.delete_refresh_token(
                    refresh_token_id=refresh_token_model.id
                )
