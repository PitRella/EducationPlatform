from typing import Any

from sqlalchemy.orm import selectinload

from src.base.dao import BaseDAO
from src.users import Author
from src.users.schemas import CreateAuthorRequestSchema
from sqlalchemy import (
    Result,
    Select,
    select,
)

class AuthorDAO(BaseDAO[Author, CreateAuthorRequestSchema]):
    async def get_author(
            self,
            *filters: Any,
            **filters_by: Any
    ) -> Author | None:
        query: Select[Any] = (
            select(self.model).where(*filters).filter_by(**filters_by).options(
                selectinload(self.model.user))
        )
        result: Result[Any] = await self.session.execute(query)
        return result.scalar_one_or_none()

