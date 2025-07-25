import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_user_from_jwt
from src.base.dependencies import get_service
from src.base.permission import BasePermissionService
from src.database import get_db
from src.users.models import User
from src.users.permissions.user import BaseUserPermission
from src.users.services import UserService


async def get_user_from_uuid(
        user_id: uuid.UUID,
        service: Annotated[UserService, Depends(get_service(UserService))],
) -> User:
    """Retrieve a User instance by UUID using the UserService dependency.

    Args:
        user_id (uuid.UUID): The unique identifier of the user.
        service (UserService, optional): Dependency-injected
        UserService instance.

    Returns:
        User: The user object corresponding to the given UUID.

    Raises:
        UserNotFoundByIdException: If no user is found with the provided UUID.

    """
    return await service.get_user_by_id(user_id=user_id)


class UserPermissionDependency:
    def __init__(self, permissions: list[type[BaseUserPermission]]):
        # Store a list of permission class types to be validated later
        self.permissions = permissions

    async def __call__(
            self,
            request: Request,
            user: Annotated[User, Depends(get_user_from_jwt)],
            db: Annotated[AsyncSession, Depends(get_db)],
    ) -> User:
        """Callable used as a FastAPI dependency. It receives the request and
        authenticated user, applies all permission classes, and raises
        if any permission fails.
        """
        for permission_cls in self.permissions:
            # Instantiate permission with request and user
            p_class = permission_cls(request=request, user=user, db=db)
            #  the actual permission check
            await p_class.validate_permission()

        # If all checks pass, return the user
        return user
