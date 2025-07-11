from typing import TypeVar, Annotated, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.service import BaseService
from src.database import get_db

Service = TypeVar('Service', bound=BaseService)


def get_service(
        service_type: type[Service],
) -> Callable[[AsyncSession], Service]:
    """Universal factory for creating service instances."""

    def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> Service:
        return service_type(db_session=db)

    return _get_service
