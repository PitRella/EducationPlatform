import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.exceptions import UserNotFoundByIdException, \
    ForgottenParametersException
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
        db: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id: Optional[uuid.UUID] = await UserService.deactivate_user(
        user_id=user_id,
        db=db
    )
    if not deleted_user_id:
        raise UserNotFoundByIdException
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
) -> ShowUser:
    user: Optional[ShowUser] = await UserService.get_user(
        user_id=user_id,
        db=db
    )
    if not user:
        raise UserNotFoundByIdException
    return user


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user(
        user_id: uuid.UUID,
        user_fields: UpdateUserRequest,
        db=Depends(get_db)
) -> UpdateUserResponse:
    filtered_user_fields: dict[str, str] = (user_fields.
                                            model_dump(exclude_none=True)
                                            )  # Delete None key value pair
    if filtered_user_fields == {}:  # If empty body
        raise UserNotFoundByIdException
    if not await get_user_by_id(user_id, db):  # If user doesn't exist
        raise ForgottenParametersException

    updated_user: Optional[UpdateUserResponse] = await (
        UserService.update_user(
            user_id,
            filtered_user_fields,
            db
        )
    )
    if not updated_user:
        raise UserNotFoundByIdException
    return updated_user
