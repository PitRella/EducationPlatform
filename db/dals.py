import uuid
from typing import Optional, Tuple, Any, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, update, Row, select

from db import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.__db_session: AsyncSession = db_session

    async def create_user(self,
                          name: str, surname: str, email: str) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.__db_session.add(new_user)
        await self.__db_session.flush()
        return new_user

    async def deactivate_user(self, user_id: uuid.UUID) -> Optional[uuid.UUID]:
        query = update(User).where(
            and_(User.user_id == user_id, User.is_active == True)).values(
            is_active=False).returning(
            User.user_id)
        result = await self.__db_session.execute(query)
        deleted_user_id_row: Optional[Row[Tuple[Any]]] = result.fetchone()
        return deleted_user_id_row[0] if deleted_user_id_row else None

    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        query = select(User).where(and_(User.user_id == user_id,
                                        User.is_active == True))
        result = await self.__db_session.execute(query)
        user: Optional[Row[Tuple[Any]]] = result.fetchone()
        return cast(User, user[0]) if user else None
