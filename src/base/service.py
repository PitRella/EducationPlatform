from typing import final

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.exceptions import ForgottenParametersException


class BaseService:
    """Base class for services."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize a new BaseService instance.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session.

        """
        self._session: AsyncSession = db_session

    @property
    def session(self) -> AsyncSession:
        """Return the current AsyncSession."""
        return self._session

    @staticmethod
    @final
    def _validate_schema_for_update_request(
            schema: BaseModel
    ) -> dict[str, str]:
        schema_fields: dict[str, str] = schema.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )  # Delete None key value pair
        if not schema_fields:
            raise ForgottenParametersException
        return schema_fields
