from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.base.dependencies import get_service
from src.users import User
from src.users.dependencies import UserPermissionDependency
from src.users.permissions import AdminPermission, SuperadminPermission
from src.users.schemas import UserResponseShema
from src.users.services import UserService

admin_router = APIRouter()


@admin_router.get('/{user_id}')
def get_user_by_id(
    user: Annotated[
        User, Security(UserPermissionDependency([AdminPermission]))
    ],
) -> UserResponseShema:
    """Get user information by their UUID if permissions allow.

    Args:
        user_id (uuid.UUID): Unique identifier of the user to retrieve
        user (User): Currently authenticated user making the request.
            Must have appropriate permissions via BaseUserPermission.

    Returns:
        UserResponseShema: Validated user data response model

    Raises:
        UserPermissionException: If an authenticated user lacks permissions,
        UserNotFoundByIdException: If no user exists with the provided UUID

    """
    return UserResponseShema.model_validate(user)


@admin_router.delete(
    '/{user_id}', description='Deactivate user by id', status_code=204
)
async def deactivate_user_by_id(
    service: Annotated[UserService, Depends(get_service(UserService))],
    user: Annotated[
        User, Security(UserPermissionDependency([AdminPermission]))
    ],
) -> None:
    """Deactivate a user account by their ID.

    Args:
        service (UserService): Service for user operations
        user (User): Target user to deactivate.
            Must be authorized via BaseUserPermission.

    Returns:
        None

    Raises:
        UserPermissionException: If caller lacks required permissions
        UserNotFoundByIdException: If target user not found

    Note:
        Sets user's is_active flag to False but does not delete the record

    """
    return await service.deactivate_user(target_user=user)


@admin_router.patch(
    '/set_admin_privilege/{user_id}',
    description='Give admin privilege to user',
    response_model=UserResponseShema,
)
async def set_admin_privilege(
    service: Annotated[UserService, Depends(get_service(UserService))],
    user: Annotated[
        User, Security(UserPermissionDependency([SuperadminPermission]))
    ],
) -> UserResponseShema:
    """Grant admin privileges to a user.

    Args:
        service (UserService): Service for user operations
        user (User): The user to be granted admin privileges.
            Must be authorized via SuperadminPermission.

    Returns:
        UserResponseShema: Updated user data after privilege grant

    Raises:
        UserPermissionException: If caller lacks required superadmin permissions
        UserNotFoundByIdException: If target user not found

    """
    updated_user = await service.set_admin_privilege(target_user=user)
    return UserResponseShema.model_validate(updated_user)


@admin_router.patch(
    '/revoke_admin_privilege/{user_id}',
    description='Revoke admin privilege from user',
    response_model=UserResponseShema,
)
async def revoke_admin_privilege(
    service: Annotated[UserService, Depends(get_service(UserService))],
    user: Annotated[
        User, Security(UserPermissionDependency([SuperadminPermission]))
    ],
) -> UserResponseShema:
    """Revoke admin privileges from a user.

    Args:
        service (UserService): Service for user operations
        user (User): The user to have admin privileges revoked.
            Must be authorized via SuperadminPermission.

    Returns:
        UserResponseShema: Updated user data after privilege revocation

    Raises:
        UserPermissionException: If caller lacks required superadmin permissions
        UserNotFoundByIdException: If target user not found

    """
    updated_user = await service.revoke_admin_privilege(target_user=user)
    return UserResponseShema.model_validate(updated_user)
