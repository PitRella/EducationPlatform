from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession

class BaseService(ABC):
    """Base class for services."""
    def __init__(self, db_session: AsyncSession) -> None:
        self._session: AsyncSession = db_session

    @property
    def session(self) -> AsyncSession:
        """Return the current AsyncSession."""
        return self._session