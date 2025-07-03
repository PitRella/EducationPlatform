from typing import Annotated

from fastapi import APIRouter, Security, Depends
from src.users.dependencies import get_service
from src.auth.dependencies import validate_user_permission
from src.users.models import User
from src.users.schemas import (
    ShowUser,
    CreateUser,
    DeleteUserResponse,
    UpdateUserResponse,
    UpdateUserRequest,
)

from src.users.service import UserService
from src.auth.enums import UserAction

user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(
    user: CreateUser,
    service: UserService = Depends(get_service),
) -> ShowUser:
    return await service.create_new_user(user=user)


@user_router.delete("/", response_model=DeleteUserResponse)
async def deactivate_user(
    service: UserService = Depends(get_service),
    user: User = Security(validate_user_permission(UserAction.DELETE)),
) -> DeleteUserResponse:
    return await service.deactivate_user(target_user=user)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
    user: Annotated[User, Security(validate_user_permission(UserAction.GET))],
) -> ShowUser:
    return ShowUser.model_validate(user)


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user(
    user: Annotated[User, Depends(validate_user_permission(UserAction.UPDATE))],
    user_fields: UpdateUserRequest,
    service: UserService = Depends(get_service),
) -> UpdateUserResponse:
    return await service.update_user(target_user=user, user_fields=user_fields)


@user_router.patch("/set_admin_privilege")
async def set_admin_privilege(
    user: Annotated[
        User, Depends(validate_user_permission(UserAction.SET_ADMIN_PRIVILEGE))
    ],
    service: UserService = Depends(get_service),
) -> UpdateUserResponse:
    return await service.set_admin_privilege(
        target_user=user,
    )


@user_router.patch("/revoke_admin_privilege")
async def revoke_admin_privilege(
    service: Annotated[UserService, Depends(get_service)],
    user: Annotated[
        User,
        Security(validate_user_permission(UserAction.REVOKE_ADMIN_PRIVILEGE)),
    ],
) -> UpdateUserResponse:
    return await service.revoke_admin_privilege(target_user=user)
