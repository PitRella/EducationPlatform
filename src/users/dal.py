import uuid
from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, update, select, Result, Select, Update
from src.users.models import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.__db_session: AsyncSession = db_session

    async def create_user(
            self,
            name: str,
            surname: str,
            email: str,
            password: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            password=password,
        )
        self.__db_session.add(new_user)
        await self.__db_session.flush()
        return new_user

    async def deactivate_user(
            self,
            user_id: uuid.UUID
    ) -> Optional[uuid.UUID]:
        user: Optional[User] = await self.get_user_by_id(user_id)
        if not user: return None
        deactivated_user_id: Optional[uuid.UUID] = await self.update_user(
            user.user_id,
            is_active=False)
        return deactivated_user_id

    async def get_user_by_id(
            self,
            user_id: uuid.UUID
    ) -> Optional[User]:
        user: Optional[User] = await self.__db_session.get(
            entity=User,
            ident=user_id
        )
        return user

    async def update_user(
            self,
            user_id: uuid.UUID,
            **kwargs
    ) -> Optional[uuid.UUID]:
        query: Update[Any] = update(User).where(
            and_(User.user_id == user_id, User.is_active == True)).values(
            kwargs).returning(User.user_id)
        result: Result[Any] = await self.__db_session.execute(query)
        updated_user_id: Optional[uuid.UUID] = result.scalar_one_or_none()
        return updated_user_id

    async def get_user_by_email(
            self,
            email: str
    ) -> Optional[User]:
        query: Select[Any] = select(User).where(User.email == email)
        result: Result[Any] = await self.__db_session.execute(query)
        user: Optional[User] = result.scalar_one_or_none()
        return user
