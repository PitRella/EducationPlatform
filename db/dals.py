import uuid
from typing import Optional, Tuple, Any, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, update, Row, select

from db import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.__db_session: AsyncSession = db_session

    async def create_user(self,
                          name: str,
                          surname: str,
                          email: str) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.__db_session.add(new_user)
        await self.__db_session.flush()
        return new_user

    async def deactivate_user(self, user_id: uuid.UUID) -> Optional[uuid.UUID]:
        user: Optional[User] = await self.__db_session.get(User, user_id)
        if user:
            user.is_active = False
            return user.user_id
        return None

    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        user: Optional[User] = await self.__db_session.get(
            entity=User,
            ident=user_id
        )
        return user
