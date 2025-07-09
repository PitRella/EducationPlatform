from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import ColumnElement, Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base

Model = TypeVar('Model', bound=Base)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
GetSchema = TypeVar('GetSchema', bound=BaseModel)
DeleteSchema = TypeVar('DeleteSchema', bound=BaseModel)


class BaseDAO[
    Model,
    CreateSchema,
    GetSchema,
    DeleteSchema,
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

    model: type[Model]

    @classmethod
    async def create_model(
        cls, session: AsyncSession, schema: BaseModel
    ) -> Model:
        """Create and save a new model instance in the database.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
            schema (CreateSchema): The Pydantic schema containing model data.

        Returns:
            Model: The created model instance.

        """
        created_model: Model = cls.model(
            **schema.model_dump(exclude_unset=True)
        )
        session.add(created_model)
        await session.flush()
        return created_model

    @classmethod
    async def get_model(
        cls,
        session: AsyncSession,
        *filters: ColumnElement[bool],
        **filters_by: Any,
    ) -> Model | None:
        """Retrieve a model instance from the database based on filters.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
            *filters (ColumnElement[bool]): Variable length filter conditions.
            **filters_by (Any): Keyword filter conditions.

        Returns:
            Model | None: Retrieved model instance or None if not found.

        """
        query: Select[Any] = (
            select(cls.model).filter(*filters).filter_by(**filters_by)
        )
        result: Result[Any] = await session.execute(query)
        return result.scalar_one_or_none()
