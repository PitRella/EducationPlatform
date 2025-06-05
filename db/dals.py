from sqlalchemy.ext.asyncio import AsyncSession
from db import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.__db_session: AsyncSession = db_session

    async def create_user(self,
                          name: str, surname: str, email: str):
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.__db_session.add(new_user)
        await self.__db_session.flush()
        return new_user
