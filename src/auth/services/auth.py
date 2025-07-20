import uuid
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import RefreshTokenException, \
    WrongCredentialsException
from src.auth.models import RefreshToken
from src.auth.schemas import CreateRefreshTokenSchema, Token
from src.auth.services.hasher import Hasher
from src.auth.services.token import TokenManager
from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.users.models import User
from src.users.schemas import CreateUserRequestSchema

type UserDAO = BaseDAO[User, CreateUserRequestSchema]
type AuthDAO = BaseDAO[RefreshToken, CreateRefreshTokenSchema]


class AuthService(BaseService):
    """Service for handling authentication-related operations.

    This service manages user authentication workflows, including
    verifying credentials, managing sessions, and interacting with
    data access objects (DAOs) for users and authentication data.

    """

    def __init__(
            self,
            db_session: AsyncSession,
            auth_dao: AuthDAO | None = None,
            user_dao: UserDAO | None = None,
    ) -> None:
        """Initialize AuthService with a database session and optional DAOs.

        This service handles user authentication, token management,
        and related operations.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session
            auth_dao (AuthDAO | None, optional): Data access object for auth
                If None, creates a new instance. Defaults to None.
            user_dao (UserDAO | None, optional): Data access object for user
                If None, creates a new instance. Defaults to None.

        Note:
            The service will create new instances of AuthDAO and UserDAO.

        """
        super().__init__(db_session)
        self._auth_dao: AuthDAO = auth_dao or BaseDAO[
            RefreshToken,
            CreateRefreshTokenSchema,
        ](session=db_session, model=RefreshToken)
        self._user_dao: UserDAO = user_dao or BaseDAO[
            User,
            CreateUserRequestSchema,
        ](session=db_session, model=User)

    @property
    def auth_dao(self) -> AuthDAO:
        """Return the AuthDAO instance."""
        return self._auth_dao

    @property
    def user_dao(self) -> UserDAO:
        """Return the UserDAO instance."""
        return self._user_dao

    @staticmethod
    def _verify_user_password(user: User | None, password: str) -> None:
        """Verify that the given password matches the user's password.

        Raise WrongCredentialsException if verification fails.
        """
        if not user or not Hasher.verify_password(password, user.password):
            raise WrongCredentialsException

    async def auth_user(self, email: str, password: str) -> User:
        """Authenticate a user by email and password.

        Fetch the user by email and verify the password.
        Raises WrongCredentialsException if authentication fails.

        Returns:
            User: Authenticated user instance.

        """
        async with self.session.begin():
            user: User | None = await self.user_dao.get_one(
                email=email,
                is_active=True
            )
        self._verify_user_password(user, password)
        return cast(User, user)

    @staticmethod
    def _get_user_id_from_jwt(decoded_jwt: dict[str, str | int]) -> str:
        """Extract and return user ID from a decoded JWT payload.

        Raises WrongCredentialsException if user ID is missing or invalid.

        Returns:
            str: User ID extracted from JWT.

        """
        user_id: int | str | None = decoded_jwt.get('sub')
        if not user_id or isinstance(user_id, int):
            raise WrongCredentialsException
        return user_id

    async def validate_token(self, user_jwt_token: str) -> User:
        """Validate a JWT token and retrieve the associated user.

        This method decodes the provided JWT token, validates its expiration,
        and retrieves the associated user from the database.

        Args:
            user_jwt_token (str): The JWT token to validate.

        Returns:
            User: The user associated with the token.

        Raises:
            WrongCredentialsException: If the token is invalid, expired,
                or the user cannot be found.

        """
        decoded_jwt: dict[str, str | int] = TokenManager.decode_access_token(
            token=user_jwt_token,
        )
        TokenManager.validate_access_token_expired(decoded_jwt)
        user_id: uuid.UUID | str = self._get_user_id_from_jwt(decoded_jwt)
        async with self.session.begin():
            user: User | None = await self.user_dao.get_one(
                id=user_id,
                is_active=True
            )
        if not user:
            raise WrongCredentialsException
        return user

    async def create_token(self, user_id: uuid.UUID) -> Token:
        """Generate new access and refresh tokens for a user.

        This method creates a new pair of tokens (access and refresh)
        for the given user,
        deletes any existing refresh tokens for that user,
         and stores the new refresh token
        in the database.

        Args:
            user_id (uuid.UUID): The unique identifier
             of the user for whom to generate tokens.

        Returns:
            Token: A Token object containing the new
            access_token and refresh_token.

        Note:
            The method will delete all existing refresh
            tokens for the user before creating
            new ones to ensure security and prevent token accumulation.

        """
        access_token: str = TokenManager.generate_access_token(user_id=user_id)
        refresh_token, tm_delta = TokenManager.generate_refresh_token()
        create_token_schema = CreateRefreshTokenSchema(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_in=tm_delta.total_seconds(),
        )
        async with self.session.begin():
            await self.auth_dao.delete(RefreshToken.user_id == user_id)
            await self.auth_dao.create(create_token_schema)
        return Token(
            access_token=access_token,
            refresh_token=str(refresh_token),
        )

    async def refresh_token(self, refresh_token: uuid.UUID) -> Token:
        """Generate new access and refresh tokens.

        This method validates the provided refresh token, checks
         if it exists and hasn't expired,
        then generates new access and refresh tokens for the user.

        Args:
        refresh_token (uuid.UUID): The current refresh token to be
        used for generating new tokens.

        Returns:
        Token: A Token object containing the new access_token and refresh_token.

        Raises:
        RefreshTokenException: If the refresh token is invalid,
        expired, or the associated user
        cannot be found.

        """
        async with self.session.begin():
            refresh_token_model: (
                    RefreshToken | None
            ) = await self.auth_dao.get_one(
                refresh_token=refresh_token,
            )
            if not refresh_token_model:
                raise RefreshTokenException
            TokenManager.validate_refresh_token_expired(
                refresh_token_model=refresh_token_model,
            )
            user_id: uuid.UUID = refresh_token_model.user_id
            user: User | None = await self.user_dao.get_one(
                id=user_id,
            )
            if not user:
                raise RefreshTokenException
            access_token: str = TokenManager.generate_access_token(
                user_id=user_id,
            )
            updated_refresh_token, tm_delta = (
                TokenManager.generate_refresh_token()
            )
            updated_refresh_token_model: (
                    RefreshToken | None
            ) = await self.auth_dao.update(
                {
                    'refresh_token': updated_refresh_token,
                    'expires_in': tm_delta.total_seconds(),
                },
                id=refresh_token_model.id,
            )
            if not updated_refresh_token_model:
                raise RefreshTokenException
            return Token(
                access_token=access_token,
                refresh_token=str(updated_refresh_token),
            )

    async def logout_user(
            self,
            refresh_token: str | None,
    ) -> None:
        """Log out a user by invalidating their refresh token.

        Args:
            refresh_token (str | None): The refresh token to invalidate.
                If None, RefreshTokenException will be raised.

        Raises:
            RefreshTokenException: If the refresh token is None or invalid.

        Returns:
            None

        """
        if not refresh_token:
            raise RefreshTokenException
        async with self.session.begin():
            refresh_token_model: (
                    RefreshToken | None
            ) = await self.auth_dao.get_one(
                refresh_token=refresh_token,
            )
            if not refresh_token_model:
                raise RefreshTokenException
            await self.auth_dao.delete(
                id=refresh_token_model.id,
            )
