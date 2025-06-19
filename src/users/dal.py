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
        """
        Create a new user in the database
        :param name: User's first name
        :param surname: User's last name
        :param email: User's email address
        :param password: User's password
        :return: Created User object
        """

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
        """
        Deactivate a user
        :param user_id: UUID of user to deactivate
        :return: Deactivated user UUID
        """
        deactivated_user_id: Optional[uuid.UUID] = await self.update_user(
            user_id,
            is_active=False
        )
        return deactivated_user_id

    async def get_user_by_id(
            self,
            user_id: Optional[uuid.UUID | str]
    ) -> Optional[User]:
        """
        Get a user by their ID
        :param user_id: UUID or string representation of user's ID
        :return: User object if found and active, None otherwise
        """

        query: Select = select(User).where(and_(
            User.user_id == user_id,
            User.is_active
        ))
        result: Result[Any] = await self.__db_session.execute(query)
        user: Optional[User] = result.scalar_one_or_none()
        return user

    async def update_user(
            self,
            user_id: uuid.UUID,
            **kwargs
    ) -> Optional[uuid.UUID]:
        """
        Update user attributes
        :param user_id: UUID of user to update
        :param kwargs: User attributes to update
        :return: Updated user UUID
        """
        query: Update = update(User).where(
            and_(User.user_id == user_id, User.is_active)).values(
            kwargs).returning(User.user_id)
        result: Result[Any] = await self.__db_session.execute(query)
        updated_user_id: Optional[uuid.UUID] = result.scalar_one_or_none()
        return updated_user_id

    async def get_user_by_email(
            self,
            email: str
    ) -> Optional[User]:
        """
        Get user by email
        :param email: User's email
        :return: User
        """
        query: Select[Any] = select(User).where(and_(
            User.email == email,
            User.is_active
        ))
        result: Result[Any] = await self.__db_session.execute(query)
        user: Optional[User] = result.scalar_one_or_none()
        return user
