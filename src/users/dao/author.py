from typing import Any

from src.base.dao import BaseDAO
from src.users import Author
from src.users.schemas import CreateAuthorRequestSchema


class AuthorDAO(BaseDAO[Author, CreateAuthorRequestSchema]):
    """Data Access Object for Author model.

    Provides methods to access Author records from the database and
    include related objects, like User.
    """

    async def get_author(
        self, *filters: Any, **filters_by: Any
    ) -> Author | None:
        """Retrieve a single Author with related User based on filters.

        Args:
            *filters (Any): Positional SQLAlchemy filter expressions.
            **filters_by (Any): Keyword filter expressions for querying.

        Returns:
            Author | None: Returns the Author instance with related User
                if found; otherwise None.

        """
        return await self.get_one_with_relations(
            *filters, relations=['user'], **filters_by
        )
