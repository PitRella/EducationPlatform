import uuid
from collections.abc import Sequence
from typing import Annotated, Literal

from fastapi import Depends
from fastapi.requests import Request

from src.auth.dependencies import _get_optional_user_from_jwt
from src.base.dependencies import BasePermissionDependency, get_service
from src.users.models import User
from src.users.permissions.user import TargetUserAdminPermission
from src.users.services import UserService


async def _get_user_by_uuid(
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


class AdminPermissionDependency(BasePermissionDependency):
    """Permission dependency for managing user access control between users.

    This class provides a FastAPI dependency that validates permissions between
    an authenticated user (source_user) and a target user for user management
    operations. It applies a list of permission classes to enforce role-based
    access control rules.

    The dependency receives:
    - The HTTP request
    - A target user (identified by UUID)
    - An authenticated source user (from JWT token)

    Validates all specified permissions by instantiating each permission class
    and calling its validate_permission() method. If any permission check fails,
    an exception is raised.

    Usage:
        @app.get("/users/{user_id}")
        async def get_user(
            user: Annotated[User, Depends(
                UserPermissionDependency([SomePermission])
            )]
        ):
            return user
    """

    def __init__(
        self,
        permissions: Sequence[type[TargetUserAdminPermission]],
        logic: Literal['AND', 'OR'] = BasePermissionDependency._LOGIC_AND,
    ):
        super().__init__(permissions, logic)

    async def __call__(
        self,
        request: Request,
        target_user: Annotated[User, Depends(_get_user_by_uuid)],
        source_user: Annotated[
            User | None, Depends(_get_optional_user_from_jwt)
        ],
    ) -> User:
        await self._validate_permissions(
            request=request, user=source_user, target_user=target_user
        )
        return target_user
