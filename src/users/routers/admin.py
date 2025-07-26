import uuid
from typing import Annotated

from fastapi import APIRouter, Security, Depends

from src.base.dependencies import get_service
from src.users import User
from src.users.dependencies import UserPermissionDependency
from src.users.permissions import BaseUserPermission, SuperadminPermission
from src.users.schemas import UserResponseShema
from src.users.services import UserService

admin_router = APIRouter()


@admin_router.get('/{user_id}')
def get_user_by_id(
        user: Annotated[
            User, Security(UserPermissionDependency([BaseUserPermission]))
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
    '/{user_id}',
    description='Deactivate user by id',
    status_code=204
)
async def deactivate_user_by_id(
        service: Annotated[UserService, Depends(get_service(UserService))],
        user: Annotated[
            User, Security(UserPermissionDependency([BaseUserPermission]))
        ],
) -> None:
    return await service.deactivate_user(target_user=user)



@admin_router.patch('/set_admin_privilege/{user_id}',
                    description='Give admin privilege to user',
                    response_model=UserResponseShema
                    )
async def set_admin_privilege(
        service: Annotated[UserService, Depends(get_service(UserService))],
        user: Annotated[
            User, Security(UserPermissionDependency([SuperadminPermission]))
        ],
) -> UserResponseShema:
    updated_user = await service.set_admin_privilege(target_user=user)
    return UserResponseShema.model_validate(updated_user)

