import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Result, Select, Update, and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.enums import UserRoles
from src.users.models import User


class UserDAO:
    """Data Access Object class for managing user-related database operations.

    This class provides an interface for interacting
    with user data in the database,
    including operations such as creating, updating,
    deactivating users, and
    managing their roles and privileges. It uses SQLAlchemy for
    database operations
    and handles both synchronous and asynchronous database queries.

    The class encapsulates all database access logic, providing a clean
    separation
    between the database layer and the business logic layer of the application.
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize UserDAO with a database session.

        :param db_session: AsyncSession object for database operations
        :type db_session: AsyncSession
        """
        self.__db_session: AsyncSession = db_session

    async def create_user(
        self,
        name: str,
        surname: str,
        email: str,
        password: str,
        user_roles: Sequence[UserRoles],
    ) -> User:
        """Create a new user in the database.

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

    async def deactivate_user(self, user_id: uuid.UUID) -> uuid.UUID | None:
        """Deactivate a user.

        :param user_id: UUID of user to deactivate
        :return: Deactivated user UUID
        """
        deactivated_user_id: uuid.UUID | None = await self.update_user(
            user_id,
            is_active=False,
        )
        return deactivated_user_id

    async def get_user_by_id(
        self,
        user_id: uuid.UUID | str | None,
    ) -> User | None:
        """Get a user by their ID.

        :param user_id: UUID or string representation of a user's ID
        :return: User object if found and active, None otherwise
        """
        query: Select = select(User).where(  # type: ignore
            and_(User.user_id == user_id, User.is_active),
        )
        result: Result[Any] = await self.__db_session.execute(query)
        user: User | None = result.scalar_one_or_none()
        return user

    async def update_user(
        self,
        user_id: uuid.UUID,
        **kwargs: Any,
    ) -> uuid.UUID | None:
        """Update a user's information in the database if the user is active.

        This method allows updating specific fields of an active user
        based on the provided keyword arguments. If the user is successfully
        updated, the unique identifier of the user is returned. If the user
        is not found or inactive, it returns None.

        :param user_id: The unique identifier of the user to be updated.
        :type user_id: uuid.UUID
        :param kwargs: The fields and their updated values to modify in the
            user's database entry.
        :type kwargs: Any
        :return: The unique identifier of the updated user if successful;
            otherwise, None.
        :rtype: uuid.UUID | None
        """
        query: Update = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active))
            .values(kwargs)
            .returning(User.user_id)
        )
        result: Result[Any] = await self.__db_session.execute(query)
        updated_user_id: uuid.UUID | None = result.scalar_one_or_none()
        return updated_user_id

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email.

        :param email: User's email
        :return: User
        """
        query: Select[Any] = select(User).where(
            and_(User.email == email, User.is_active),
        )
        result: Result[Any] = await self.__db_session.execute(query)
        user: User | None = result.scalar_one_or_none()
        return user

    async def set_admin_privilege(
        self,
        target_user_id: uuid.UUID,
    ) -> uuid.UUID | None:
        """Grant admin privileges to a user.

        :param target_user_id: UUID of user to grant admin privileges to
        :return: Updated user UUID if successful, None otherwise
        """
        return await self.update_user(target_user_id, roles=[UserRoles.ADMIN])

    async def revoke_admin_privilege(
        self,
        target_user_id: uuid.UUID,
    ) -> uuid.UUID | None:
        """Revoke admin privileges from a user.

        :param target_user_id: UUID of user to revoke admin privileges from
        :return: Updated user UUID if successful, None otherwise
        """
        return await self.update_user(target_user_id, roles=[UserRoles.USER])
