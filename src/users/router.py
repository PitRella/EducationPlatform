import uuid

from fastapi import APIRouter, Depends
from .dependencies import get_service
from src.auth.dependencies import get_user_from_jwt, validate_user_permission
from src.users.models import User
from src.users.schemas import (
    ShowUser,
    CreateUser,
    DeleteUserResponse,
    UpdateUserResponse,
    UpdateUserRequest,
)

from src.users.service import UserService
from ..auth.enums import UserAction

user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(
    user: CreateUser,
    service: UserService = Depends(get_service),
) -> ShowUser:
    return await service.create_new_user(user=user)


@user_router.delete("/", response_model=DeleteUserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_service),
    jwt_user: User = Depends(get_user_from_jwt),
) -> DeleteUserResponse:
    return await service.deactivate_user(
        requested_user_id=user_id, jwt_user=jwt_user
    )


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
    user: User = Depends(validate_user_permission(UserAction.GET)),
) -> ShowUser:
    return ShowUser.model_validate(user)


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_fields: UpdateUserRequest,
    service: UserService = Depends(get_service),
    jwt_user: User = Depends(get_user_from_jwt),
) -> UpdateUserResponse:
    return await service.update_user(
        jwt_user=jwt_user, requested_user_id=user_id, user_fields=user_fields
    )


@user_router.patch("/set_admin_privilege")
async def set_admin_privilege(
    user_id: uuid.UUID,
    service: UserService = Depends(get_service),
    jwt_user: User = Depends(get_user_from_jwt),
) -> UpdateUserResponse:
    return await service.set_admin_privilege(
        jwt_user=jwt_user,
        requested_user_id=user_id,
    )


@user_router.patch("/revoke_admin_privilege")
async def revoke_admin_privilege(
    user_id: uuid.UUID,
    service: UserService = Depends(get_service),
    jwt_user: User = Depends(get_user_from_jwt),
) -> UpdateUserResponse:
    return await service.revoke_admin_privilege(
        jwt_user=jwt_user,
        requested_user_id=user_id,
    )
