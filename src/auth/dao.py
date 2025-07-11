import uuid

from sqlalchemy import Delete, Result, Select, Update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import RefreshToken


class AuthDAO:
    """Database Access Layer for authentication operations.

    This class handles all database operations related to authentication:
    - Creating refresh tokens
    - Retrieving refresh tokens
    - Updating refresh tokens
    - Deleting refresh tokens

    Attributes:
        __db_session (AsyncSession): The database session.

    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the AuthDAO with a database session.

        Args:
            db_session (AsyncSession): Async database session for queries.

        """
        self.__db_session: AsyncSession = db_session

    async def delete_old_tokens(
        self,
        user_id: uuid.UUID,
    ) -> None:
        """Delete all refresh tokens associated with the given user ID.

        Args:
            user_id (uuid.UUID): The ID of the user whose tokens to delete.

        """
        query: Delete = Delete(RefreshToken).where(
            RefreshToken.user_id == user_id,
        )
        await self.__db_session.execute(query)

    async def create_token(
        self,
        user_id: uuid.UUID,
        refresh_token: uuid.UUID,
        refresh_token_expires_total_seconds: float,
    ) -> RefreshToken | None:
        """Create a new refresh token session for a user.

        Args:
            user_id (uuid.UUID): The ID of the user for whom token.
            refresh_token (uuid.UUID): The new refresh token value.
            refresh_token_expires_total_seconds (float): Token expiration time.

        Returns:
            RefreshToken | None: The newly created refresh session model.

        """
        new_token = RefreshToken(
            refresh_token=refresh_token,
            expires_in=refresh_token_expires_total_seconds,
            user_id=user_id,
        )
        self.__db_session.add(new_token)
        return new_token

    async def get_refresh_token(
        self,
        refresh_token: uuid.UUID | str,
    ) -> RefreshToken | None:
        """Retrieve a refresh token session by its token value.

        Args:
            refresh_token (uuid.UUID | str): The refresh token to look up.

        Returns:
            RefreshToken | None: The matching refresh session.

        """
        query: Select[RefreshToken] = Select(RefreshToken).where(
            RefreshToken.refresh_token == refresh_token,
        )
        result: Result = await self.__db_session.execute(query)  
        token: RefreshToken | None = result.scalar_one_or_none()
        return token

    async def update_refresh_token(
        self,
        refresh_token_id: int,
        refresh_token: uuid.UUID,
        expires_at: float,
    ) -> RefreshToken | None:
        """Update an existing refresh token and its expiration.

        Args:
            refresh_token_id (int): The ID of the refresh token to update.
            refresh_token (uuid.UUID): The new refresh token value.
            expires_at (float): The new expiration time.

        Returns:
            RefreshToken | None: The updated refresh session

        """
        query: Update = (
            Update(RefreshToken)
            .where(RefreshToken.id == refresh_token_id)
            .values(refresh_token=refresh_token, expires_in=expires_at)
            .returning(RefreshToken.id)
        )
        result: Result[RefreshToken] = await self.__db_session.execute(  # type: ignore
            query,
        )
        updated_token: RefreshToken | None = result.scalar_one_or_none()
        return updated_token

    async def delete_refresh_token(self, refresh_token_id: int) -> None:
        """Delete a refresh token session by its ID.

        Args:
            refresh_token_id (int): The ID of the refresh token to delete.

        """
        query: Delete = Delete(RefreshToken).where(
            RefreshToken.id == refresh_token_id,
        )
        await self.__db_session.execute(query)
