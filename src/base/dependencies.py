from collections.abc import Callable
from typing import Annotated, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.service import BaseService
from src.database import get_db

Service = TypeVar('Service', bound=BaseService)


def get_service[Service](
    service_type: type[Service],
) -> Callable[[AsyncSession], Service]:
    """Create a FastAPI dependency for service injection using factory.

    Creates a dependency that will instantiate and provide the specified
    service type with an injected database session.

    Args:
        service_type: The class type of the service to instantiate.
         Must be a subclass of BaseService.

    Returns:
        A callable dependency that will provide an instance
        of the specified service type when injected.

    Example:
        @router.get("/")
        async def endpoint(service: Annotated[UserService,
            Depends(get_service(UserService))]):
            return await service.some_method()

    """

    def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> Service:
        return service_type(db_session=db)  # type: ignore

    return _get_service
