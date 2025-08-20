from collections.abc import Callable
from typing import Annotated, TypeVar, Unpack

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from src.base.permission import BasePermission, PermissionKwargs
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


class BasePermissionDependency:
    def __init__(self, permissions: list[type[BasePermission]]):
        self.permissions = permissions

    async def _validate_permissions(
            self,
            request: Request,
            **context: Unpack[PermissionKwargs]
    ) -> None:
        for permission_cls in self.permissions:
            permission_instance = permission_cls(request=request, **context)
            await permission_instance.validate_permission()
