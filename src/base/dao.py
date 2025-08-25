import datetime as dt
import uuid
from typing import Any, TypeVar, cast

from pydantic import BaseModel
from sqlalchemy import (
    Delete,
    Result,
    Select,
    Update,
    and_,
    desc,
    or_,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import Base

Model = TypeVar('Model', bound=Base)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)


class BaseDAO[
Model,
CreateSchema = None,
]:
    """Base Data Access Object class providing common database operations.

    Generic Type Parameters:
        Model: SQLAlchemy model class derived from Base
        CreateSchema: Pydantic model for create operations
        GetSchema: Pydantic model for get operations
        DeleteSchema: Pydantic model for delete operations

    This class implements basic CRUD operations using SQLAlchemy async
    session and Pydantic schemas for data validation.
    """

    def __init__(self, session: AsyncSession, model: type[Model]):
        """Initialize a new BaseDAO instance."""
        self._session: AsyncSession = session
        self._model: type[Model] = model

    @property
    def session(self) -> AsyncSession:
        """Return the current database session."""
        return self._session

    @property
    def model(self) -> type[Model]:
        """Return the current model for dao."""
        return self._model

    async def create(self, data: CreateSchema | dict[str, Any]) -> Model:
        """Create a new database record using provided data.

        Args:
            data: Either a Pydantic model instance or a dictionary containing
                 the data for creating a new record. Dictionary input is used
                 for special cases like creating a user with hashed password.

        Returns:
            Model: The newly created database model instance.

        Note:
            The method adds the created model to the session but does not commit
            the transaction. The caller is responsible for that.

        """
        # For rare cases like to create a user with hash pass
        if isinstance(data, dict):
            created_model = self.model(**data)
            self.session.add(created_model)
            return created_model
        # Cast to show mypy that our schema has a model_dump method
        created_model = self.model(
            **cast(BaseModel, data).model_dump(exclude_unset=True)
        )
        self.session.add(created_model)
        return created_model

    async def _get(self, *filters: Any, **filters_by: Any) -> Result[Any]:
        """Execute a database query with the specified filters.

        Method that constructs and executes a SELECT query with filters.

        Args:
            *filters: Variable length argument list of filter conditions
            **filters_by: Arbitrary kwargs for filtering by column values

        Returns:
            Result[Any]: SQLAlchemy Result object containing the query results

        """
        query: Select[Any] = (
            select(self.model).where(*filters).filter_by(**filters_by)
        )
        return await self.session.execute(query)

    async def get_one(self, *filters: Any, **filters_by: Any) -> Model | None:
        """Retrieve a single record matching the specified filters.

        Args:
            *filters: Variable length argument list of filter conditions
            **filters_by: Arbitrary kwargs for filtering by column values

        Returns:
            Model | None: Model instance matching the filters or None

        """
        result: Result[Any] = await self._get(*filters, **filters_by)
        return result.scalar_one_or_none()

    async def get_one_with_relations(
            self,
            relations: list[str],
            *filters: Any,
            **filters_by: Any
    ) -> Model | None:
        options = [
            selectinload(getattr(self.model, relation)) for relation in
            relations
        ]
        query: Select[Any] = (
            select(self.model)
            .where(*filters)
            .filter_by(**filters_by)
            .options(*options)
        )
        result: Result[Any] = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
            self,
            created_at: dt.datetime | None = None,
            last_id: uuid.UUID | None = None,
            limit: int | None = None,
            order_by: list[str] | None = None,
            *filters: Any,
            **filters_by: Any,
    ) -> list[Model] | None:
        """Retrieve all records matching the specified filters.

        Args:
            last_id: Optional UUID for filtering by last_id, for pagination
            created_at: Optional datetime object for filtering by created_at
            limit: Optional num for limiting the number of results returned.
            order_by: Optional list of columns to order by.
            *filters: Variable length argument list of filter conditions
            **filters_by: Arbitrary kwargs for filtering by column values

        Returns:
            list[Model] | None: List of model instances matching the filters

        """
        pagination = []
        if created_at and last_id:
            pagination = [
                or_(
                    self.model.created_at < created_at,  # type: ignore
                    and_(
                        self.model.created_at == created_at,  # type: ignore
                        self.model.id < last_id,  # type: ignore
                    ),
                )
            ]
        query: Select[Any] = (
            select(self.model)
            .where(*filters, *pagination)
            .filter_by(**filters_by)
            .order_by(
                desc(*order_by),  # type: ignore
                desc(self.model.created_at),  # type: ignore
                desc(self.model.id),  # type: ignore
            )
        )
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return cast(list[Model], result.scalars().all())

    async def update(
            self,
            update_data: dict[str, Any],
            *filters: Any,
            **filters_by: Any,
    ) -> Model | None:
        """Update records matching the specified filters with provided data.

        Args:
            update_data: Pydantic model containing the fields to update
            *filters: Variable length argument list of filter conditions
            **filters_by: Arbitrary kwargs for filtering by column values

        Returns:
            Model | None: Updated model instance or None

        """
        query: Update = (
            update(self.model)
            .where(*filters)
            .filter_by(**filters_by)
            .values(update_data)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(
            self,
            *filters: Any,
            **filters_by: Any,
    ) -> None:
        """Delete records matching the specified filters.

        Args:
            *filters: Variable length argument list of filter conditions
            **filters_by: Arbitrary kwargs for filtering by column values

        Note:
            The method executes the delete query but does not commit
            the transaction. The caller is responsible for that.

        """
        query: Delete = (
            Delete(self.model).where(*filters).filter_by(**filters_by)
        )
        await self.session.execute(query)
