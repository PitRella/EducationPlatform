import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.users import User
from src.users.exceptions.author import (
    AdminCannotBeAuthorException,
    UserIsNotAuthorException,
)
from src.users.models import Author
from src.users.schemas import CreateAuthorRequestSchema
from src.utils import make_slug

type AuthorDAO = BaseDAO[Author, CreateAuthorRequestSchema]


class AuthorService(BaseService):
    """Service class for managing author-related operations.

    Provides methods to check if a user is a verified author.
    Methods to create a new author profile for eligible users.
    Handles validation and business logic for author creation,
    ensuring only non-admin users can become authors.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        dao: AuthorDAO | None = None,
    ) -> None:
        """Initialize a new UserService instance.

        Args:
            db_session (AsyncSession): The SQLAlchemy async session
            dao (UserDAO | None, optional): Data Access Object
             for user operations.
                If None, creates a new UserDAO instance.
                Defaults to None.

        """
        super().__init__(db_session)
        self._dao: AuthorDAO = dao or BaseDAO[
            Author, CreateAuthorRequestSchema
        ](session=db_session, model=Author)

    async def get_author_by_user_id(self, user_id: uuid.UUID | str) -> Author:
        """Check if a user is a verified author.

        Args:
            user_id (uuid.UUID | str): The ID of the user to check.

        Returns:
            Author: The verified Author instance.

        Raises:
            UserIsNotAuthorException: If the user is not a verified author.

        """
        async with self.session.begin():
            author: Author | None = await self._dao.get_one(
                user_id=user_id, is_verified=True
            )
        if not author:
            raise UserIsNotAuthorException
        return author

    async def get_author_by_id(self, author_id: uuid.UUID | str) -> Author:

        async with self.session.begin():
            author: Author | None = await self._dao.get_one(
                id=author_id, is_verified=True
            )
        if not author:
            raise UserIsNotAuthorException
        return author

    async def become_author(
        self, user: User, author_schema: CreateAuthorRequestSchema
    ) -> Author:
        """Create a new Author for a user if they are not in the admin group.

        Args:
            user (User): The user attempting to become an author.
            author_schema (CreateAuthorRequestSchema): Schema with author data.

        Returns:
            Author: The newly created Author instance.

        Raises:
            AdminCannotBeAuthorException: If the user is an admin or superadmin.

        """
        if user.is_user_in_admin_group:
            raise AdminCannotBeAuthorException
        user_data: dict[str, Any] = author_schema.model_dump(mode='json')
        user_data['user_id'] = user.id
        user_data['slug'] = make_slug(user.name or user.surname)
        async with self.session.begin():
            new_author: Author = await self._dao.create(user_data)
        return new_author
