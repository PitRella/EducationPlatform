import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import ShowUser, CreateUser, DeleteUserResponse
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
