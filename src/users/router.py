import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.router import get_user_from_jwt
from src.users.models import User
from src.users.schemas import (
    ShowUser,
    CreateUser,
    DeleteUserResponse,
    UpdateUserResponse,
    UpdateUserRequest
)
from src.session import get_db

from src.users.service import UserService

user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(
        user: CreateUser,
        db: AsyncSession = Depends(get_db)
) -> ShowUser:
    return await UserService.create_new_user(
        user=user,
        db=db
    )


@user_router.delete("/", response_model=DeleteUserResponse)
async def deactivate_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        jwt_user: User = Depends(get_user_from_jwt),

) -> DeleteUserResponse:
    deleted_user: DeleteUserResponse = await UserService.deactivate_user(
        requested_user_id=user_id,
        jwt_user_id=jwt_user.user_id,
        db=db
    )
    return deleted_user


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        jwt_user: User = Depends(get_user_from_jwt),

) -> ShowUser:
    user: ShowUser = await UserService.get_user(
        jwt_user_id=jwt_user.user_id,
        requested_user_id=user_id,
        db=db
    )
    return user


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user(
        user_id: uuid.UUID,
        user_fields: UpdateUserRequest,
        db=Depends(get_db),
        jwt_user: User = Depends(get_user_from_jwt),

) -> UpdateUserResponse:
    updated_user: UpdateUserResponse = await (
        UserService.update_user(
            jwt_user_id=jwt_user.user_id,
            requested_user_id=user_id,
            user_fields=user_fields,
            db=db
        )
    )
    return updated_user
