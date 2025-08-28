from typing import Any

from src.base.dao import BaseDAO
from src.users import Author
from src.users.schemas import CreateAuthorRequestSchema


class AuthorDAO(BaseDAO[Author, CreateAuthorRequestSchema]):
    async def get_author(
        self, *filters: Any, **filters_by: Any
    ) -> Author | None:
        return await self.get_one_with_relations(
            *filters, relations=['user'], **filters_by
        )
