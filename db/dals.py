import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, update

from db import User


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
        user: Optional[User] = await self.get_user(user_id)
        if not user: return None
        deactivated_user_id: Optional[uuid.UUID] = await self.update_user(
            user.user_id,
            is_active=False)
        return deactivated_user_id

    async def get_user(
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
        query = update(User).where(
            and_(User.user_id == user_id, User.is_active == True)).values(
            kwargs).returning(User.user_id)
        result = await self.__db_session.execute(query)
        updated_user_id: Optional[uuid.UUID] = result.scalar_one_or_none()
        return updated_user_id
