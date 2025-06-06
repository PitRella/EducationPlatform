import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.base import state_str

from api.models import ShowUser, CreateUser, DeleteUserResponse, \
    UpdateUserResponse, UpdateUserRequest
from db import User
from db.dals import UserDAL
from db.session import get_db
from fastapi import HTTPException

user_router = APIRouter()


async def _create_new_user(user: CreateUser, db: AsyncSession) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            created_user: User = await user_dal.create_user(
                name=user.name,
                surname=user.surname,
                email=user.email
            )
            return ShowUser(
                user_id=created_user.user_id,  # type: ignore
                name=created_user.name,  # type: ignore
                surname=created_user.surname,  # type: ignore
                email=created_user.email,  # type: ignore
                is_active=created_user.is_active,  # type: ignore
            )


async def _deactivate_user(user_id: uuid.UUID, db: AsyncSession) -> \
        Optional[
            uuid.UUID]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            deleted_user_id: Optional[
                uuid.UUID] = await user_dal.deactivate_user(
                user_id)
            return deleted_user_id


async def _get_user(user_id: uuid.UUID, db: AsyncSession) -> Optional[
    ShowUser]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user: Optional[User] = await user_dal.get_user(user_id)
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            ) if user else None


async def __update_user(
        user_id: uuid.UUID,
        user_fields: UpdateUserRequest,
        db: AsyncSession
) -> Optional[UpdateUserResponse]:
    async with (db as session):
        async with session.begin():
            user_dal = UserDAL(db)
            updated_user_id: Optional[uuid.UUID] = await user_dal.update_user(
                user_id,
                **user_fields.model_dump()
            )
            return UpdateUserResponse(
                updated_user_id=updated_user_id) if updated_user_id else None


@user_router.post("/", response_model=ShowUser)
async def create_user(
        user: CreateUser,
        db: AsyncSession = Depends(get_db)
) -> ShowUser:
    return await _create_new_user(user, db)


@user_router.delete("/", response_model=DeleteUserResponse)
async def deactivate_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id: Optional[uuid.UUID] = await _deactivate_user(user_id, db)
    if not deleted_user_id:
        raise HTTPException(status_code=404,
                            detail=f"User with {deleted_user_id} not found.")
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
) -> ShowUser:
    user: Optional[ShowUser] = await _get_user(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail=f"Active user with"
                                                    f" {user_id} "
                                                    f"not found.")
    return user


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user(
        user_id: uuid.UUID,
        user_fields: UpdateUserRequest,
        db=Depends(get_db)
) -> UpdateUserResponse:
    if user_fields.model_dump(exclude_none=True) == {}:  # If empty body
        raise HTTPException(status_code=422, detail=f"At least one parameter "
                                                    f"for user update info "
                                                    f"should be provided")
    if not await get_user_by_id(user_id, db):  # If user doesn't exist
        raise HTTPException(status_code=404, detail=f"Active user with "
                                                    f"{user_id} cannot be "
                                                    f"found and updated")

    updated_user: Optional[UpdateUserResponse] = await __update_user(
        user_id,
        user_fields,
        db
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail=f"Active user with "
                                                    f"{user_id} cannot be "
                                                    f"found and updated")
    return updated_user
