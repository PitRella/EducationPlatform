from typing import TypeVar, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.service import BaseService
from src.database import get_db

Service = TypeVar('Service', bound=BaseService)


def get_service(
        service_type: type[Service],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> Service:
    """Universal factory for creating service instances."""
    return service_type(db_session=db)
