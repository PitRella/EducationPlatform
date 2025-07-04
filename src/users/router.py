from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.auth.dependencies import validate_user_permission
from src.auth.enums import UserAction
from src.users.dependencies import get_service
from src.users.models import User
from src.users.schemas import (
    CreateUser,
    DeleteUserResponse,
    ShowUser,
    UpdateUserRequest,
    UpdateUserResponse,
)
from src.users.service import UserService

user_router = APIRouter()


@user_router.post('/', response_model=ShowUser)
async def create_user(
    user: CreateUser,
    service: Annotated[UserService, Depends(get_service)],
) -> ShowUser:
    """Endpoint to create a new user."""
    return await service.create_new_user(user=user)


@user_router.delete('/', response_model=DeleteUserResponse)
async def deactivate_user(
    service: Annotated[UserService, Depends(get_service)],
    user: Annotated[User, Security(validate_user_permission(UserAction.GET))],
) -> DeleteUserResponse:
    """Endpoint to deactivate the user."""
    return await service.deactivate_user(target_user=user)


@user_router.get('/', response_model=ShowUser)
async def get_user_by_id(
    user: Annotated[User, Security(validate_user_permission(UserAction.GET))],
) -> ShowUser:
    """Endpoint to update get a user."""
    return ShowUser.model_validate(user)


@user_router.patch('/', response_model=UpdateUserResponse)
async def update_user(
    user: Annotated[User, Depends(validate_user_permission(UserAction.UPDATE))],
    user_fields: UpdateUserRequest,
    service: Annotated[UserService, Depends(get_service)],
) -> UpdateUserResponse:
    """Endpoint to update info about a user."""
    return await service.update_user(target_user=user, user_fields=user_fields)


@user_router.patch('/set_admin_privilege')
async def set_admin_privilege(
    user: Annotated[
        User,
        Depends(validate_user_permission(UserAction.SET_ADMIN_PRIVILEGE)),
    ],
    service: Annotated[UserService, Depends(get_service)],
) -> UpdateUserResponse:
    """Endpoint to set admin privileges to a user."""
    return await service.set_admin_privilege(
        target_user=user,
    )


@user_router.patch('/revoke_admin_privilege')
async def revoke_admin_privilege(
    service: Annotated[UserService, Depends(get_service)],
    user: Annotated[
        User,
        Security(validate_user_permission(UserAction.REVOKE_ADMIN_PRIVILEGE)),
    ],
) -> UpdateUserResponse:
    """Endpoint to revoke admin privileges from a user."""
    return await service.revoke_admin_privilege(target_user=user)
