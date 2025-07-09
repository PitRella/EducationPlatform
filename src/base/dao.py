from typing import TypeVar, cast

from pydantic import BaseModel
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

    async def create_model(self, schema: CreateSchema) -> Model:
        """Create and save a new model instance in the database.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
            schema (CreateSchema): The Pydantic schema containing model data.

        Returns:
            Model: The created model instance.

        """
        # Use cast to show mypy that our schema is inherited from BaseModel
        created_model: Model = self.model(
            **cast(BaseModel, schema).model_dump(exclude_unset=True)
        )
        self.session.add(created_model)
        return created_model
