from collections.abc import Callable, Sequence
from typing import Annotated, Literal, TypeVar, Unpack

from fastapi import Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

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
    """Handles validation of multiple permission classes with AND/OR logic.

    This class allows composing multiple permission checks for a request,
    and supports validating all or any permissions based on the logic.
    """

    _LOGIC_AND: Literal['AND'] = 'AND'
    _LOGIC_OR: Literal['OR'] = 'OR'

    def __init__(
        self,
        permissions: Sequence[type[BasePermission]],
        logic: Literal['AND', 'OR'] = _LOGIC_AND,
    ):
        """Initialize permission dependency with logic and permissions.

        Args:
            permissions (Sequence[type[BasePermission]]): List of permission
                classes to validate.
            logic (Literal['AND', 'OR'], optional): Validation logic.
                Defaults to 'AND'.

        """
        self.permissions = permissions
        self.logic: Literal['AND', 'OR'] = logic

    async def _validate_permissions(
        self, request: Request, **context: Unpack[PermissionKwargs]
    ) -> None:
        """Validate permissions according to the configured logic.

        Args:
            request (Request): The current HTTP request.
            **context (PermissionKwargs): Context for permission checks.

        Raises:
            Exception: If the permissions are not satisfied based on logic.

        """
        match self.logic:
            case self._LOGIC_AND:
                await self._validate_all_permissions(request, **context)
            case self._LOGIC_OR:
                await self._validate_any_permissions(request, **context)

    async def _validate_all_permissions(
        self, request: Request, **context: Unpack[PermissionKwargs]
    ) -> None:
        """Validate that all permissions are satisfied.

        Args:
            request (Request): The current HTTP request.
            **context (PermissionKwargs): Context for permission checks.

        Raises:
            Exception: If any permission is not satisfied.

        """
        for permission_cls in self.permissions:
            permission_instance = permission_cls(request=request, **context)
            await permission_instance.validate_permission()

    async def _validate_any_permissions(
        self, request: Request, **context: Unpack[PermissionKwargs]
    ) -> None:
        """Validate that at least one permission is satisfied.

        Args:
            request (Request): The current HTTP request.
            **context (PermissionKwargs): Context for permission checks.

        Raises:
            Exception: If none of the permissions are satisfied.

        """
        errors: list[str] = []
        for permission_cls in self.permissions:
            try:
                permission_instance = permission_cls(request=request, **context)
                await permission_instance.validate_permission()
                return  # At least one permission satisfied
            except Exception as e:
                errors.append(f'{permission_cls.__name__}: {e!s}')
        raise Exception(
            f'None of the permissions were satisfied: {"; ".join(errors)}'
        )
