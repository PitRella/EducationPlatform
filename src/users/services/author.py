from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.users import User
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

    async def create_new_author(self, user: User):
        print(f'create_new_author, {user}')
