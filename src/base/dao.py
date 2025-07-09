from typing import Any, TypeVar, cast

from pydantic import BaseModel
from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base

Model = TypeVar('Model', bound=Base)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)


class BaseDAO[
    Model,
    CreateSchema,
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

    async def create(self, schema: CreateSchema) -> Model:
        """Create a new database record from the provided schema.

        Args:
            schema (CreateSchema): Pydantic model instance containing the data
                for the new record.

        Returns:
            Model: Created database model instance.

        """
        # Use cast to show mypy that our schema is inherited from BaseModel
        created_model: Model = self.model(
            **cast(BaseModel, schema).model_dump(exclude_unset=True)
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
            select(self.model).filter(*filters).filter_by(**filters_by)
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

    async def get_all(
        self, *filters: Any, **filters_by: Any
    ) -> list[Model] | None:
        """Retrieve all records matching the specified filters.

        Args:
            *filters: Variable length argument list of filter conditions
            **filters_by: Arbitrary kwargs for filtering by column values

        Returns:
            list[Model] | None: List of model instances matching the filters

        """
        result: Result[Any] = await self._get(*filters, **filters_by)
        return cast(list[Model], result.scalars().all())
