from typing import Any

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.users import User
from src.users.exceptions.author import AdminCannotBeAuthorException
from src.users.models import Author
from src.users.schemas import CreateAuthorRequestSchema

type AuthorDAO = BaseDAO[Author, CreateAuthorRequestSchema]


class AuthorService(BaseService):
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

    async def become_author(
            self,
            user: User,
            author_schema: CreateAuthorRequestSchema
    ) -> CreateAuthorRequestSchema:
        if user.is_user_in_admin_group:
            raise AdminCannotBeAuthorException
        user_data: dict[str, Any] = author_schema.model_dump(mode="json")
        user_data['user_id'] = user.id
        user_data["slug"] = slugify(str(user.name or user.surname))

        async with self.session.begin():
            new_author: Author = await self._dao.create(user_data)
        return CreateAuthorRequestSchema.model_validate(new_author)