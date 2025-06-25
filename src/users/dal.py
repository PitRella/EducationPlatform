import uuid
from typing import Optional, Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, update, select, Result, Select, Update
from src.users.models import User
from src.users.enums import UserRoles


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.__db_session: AsyncSession = db_session

    async def create_user(
        self,
        name: str,
        surname: str,
        email: str,
        password: str,
        user_roles: Sequence[UserRoles],
    ) -> User:
        """
        Create a new user in the database
        :param name: User's first name
        :param surname: User's last name
        :param email: User's email address
        :param password: User's password
        :param user_roles: List of roles assigned to the user
        :return: Created User object
        """

        new_user = User(
            name=name,
            surname=surname,
            email=email,
            password=password,
            roles=[r.value for r in user_roles],
            # Convert from sequence to str
        )
        self.__db_session.add(new_user)
        await self.__db_session.flush()
        return new_user

    async def deactivate_user(self, user_id: uuid.UUID) -> Optional[uuid.UUID]:
        """
        Deactivate a user
        :param user_id: UUID of user to deactivate
        :return: Deactivated user UUID
        """
        deactivated_user_id: Optional[uuid.UUID] = await self.update_user(
            user_id, is_active=False
        )
        return deactivated_user_id

    async def get_user_by_id(
        self, user_id: Optional[uuid.UUID | str]
    ) -> Optional[User]:
        """
        Get a user by their ID
        :param user_id: UUID or string representation of a user's ID
        :return: User object if found and active, None otherwise
        """

        query: Select = select(User).where(  # type: ignore
            and_(User.user_id == user_id, User.is_active)
        )
        result: Result[Any] = await self.__db_session.execute(query)
        user: Optional[User] = result.scalar_one_or_none()
        return user

    async def update_user(
        self, user_id: uuid.UUID, **kwargs: Any
    ) -> Optional[uuid.UUID]:
        """
        Update user attributes in the database
        :param user_id: UUID of user to update
        :param kwargs: Arbitrary keyword arguments representing user attributes to update
        :return: Updated user UUID if successful, None otherwise
        """
        query: Update = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active))
            .values(kwargs)
            .returning(User.user_id)
        )
        result: Result[Any] = await self.__db_session.execute(query)
        updated_user_id: Optional[uuid.UUID] = result.scalar_one_or_none()
        return updated_user_id

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        :param email: User's email
        :return: User
        """
        query: Select[Any] = select(User).where(
            and_(User.email == email, User.is_active)
        )
        result: Result[Any] = await self.__db_session.execute(query)
        user: Optional[User] = result.scalar_one_or_none()
        return user

    async def set_admin_privilege(
        self, target_user_id: uuid.UUID
    ) -> Optional[uuid.UUID]:
        return await self.update_user(target_user_id, roles=[UserRoles.ADMIN])

    async def revoke_admin_privilege(
        self, target_user_id: uuid.UUID
    ) -> Optional[uuid.UUID]:
        return await self.update_user(target_user_id, roles=[UserRoles.USER])
