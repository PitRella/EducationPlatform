import uuid
from typing import Optional

from src.users.dal import UserDAL
from src.hashing import Hasher
from src.users.models import User
from src.users.schemas import CreateUser, ShowUser, UpdateUserResponse
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:

    @classmethod
    async def create_new_user(
            cls,
            user: CreateUser,
            db: AsyncSession
    ) -> ShowUser:
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                created_user: User = await user_dal.create_user(
                    name=user.name,
                    surname=user.surname,
                    email=user.email,
                    password=Hasher.hash_password(user.password)
                )
                return ShowUser(
                    user_id=created_user.user_id,
                    name=created_user.name,
                    surname=created_user.surname,
                    email=created_user.email,
                    is_active=created_user.is_active,
                )

    @classmethod
    async def deactivate_user(
            cls,
            user_id: uuid.UUID,
            db: AsyncSession
    ) -> \
            Optional[
                uuid.UUID]:
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                deleted_user_id: Optional[
                    uuid.UUID] = await user_dal.deactivate_user(
                    user_id)
                return deleted_user_id

    @classmethod
    async def get_user(
            cls,
            user_id: uuid.UUID,
            db: AsyncSession
    ) -> Optional[ShowUser]:
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_id(user_id)
                return ShowUser(
                    user_id=user.user_id,
                    name=user.name,
                    surname=user.surname,
                    email=user.email,
                    is_active=user.is_active,
                ) if user else None

    @classmethod
    async def update_user(
            cls,
            user_id: uuid.UUID,
            user_fields: dict[str, str],
            db: AsyncSession
    ) -> Optional[UpdateUserResponse]:
        async with (db as session):
            async with session.begin():
                user_dal = UserDAL(db)
                updated_user_id: Optional[
                    uuid.UUID] = await user_dal.update_user(
                    user_id,
                    **user_fields,
                )
                return UpdateUserResponse(
                    updated_user_id=updated_user_id) if updated_user_id else None
