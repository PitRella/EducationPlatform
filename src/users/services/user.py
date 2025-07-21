import uuid
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.hasher import Hasher
from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.users.exceptions import (
    UserNotFoundByIdException,
)
from src.users.models import User
from src.users.schemas import (
    CreateUserRequestSchema,
    UpdateUserRequestSchema,
)

type UserDAO = BaseDAO[User, CreateUserRequestSchema]


class UserService(BaseService):
    """Service class for handling user-related business logic and operations.

    This class provides an interface between the API layer
    and data access layer,
    implementing business logic for user management operations
    such as creation, retrieval, updates, and privilege management.

    Attributes:
        _session (AsyncSession): SQLAlchemy async session.
        _dao (UserDAO): Data Access Object for user-related db operations

    The service handles:
        - User creation and retrieval
        - User information updates
        - User deactivation
        - Admin privilege management
        - Input validation and error handling

    """

    _DEACTIVATE_USER_UPDATE: ClassVar[dict[str, bool]] = {'is_active': False}
    _REVOKE_ADMIN_UPDATE: ClassVar[dict[str, list[str]]] = {'roles': ['user']}
    _SET_ADMIN_UPDATE: ClassVar[dict[str, list[str]]] = {'roles': ['admin']}

    def __init__(
        self,
        db_session: AsyncSession,
        dao: UserDAO | None = None,
    ) -> None:
        """Initialize a new UserService instance.

        Args:
            db_session (AsyncSession): The SQLAlchemy async session
            dao (UserDAO | None, optional): Data Access Object
             for user operations.
                If None, creates a new UserDAO instance.
                Defaults to None.

        """
        super().__init__(db_session)
        self._dao: UserDAO = dao or BaseDAO[
            User,
            CreateUserRequestSchema,
        ](session=db_session, model=User)

    @property
    def dao(self) -> UserDAO:
        """Get the data access object associated with this service.

        Returns:
            UserDAO: The Data Access Object for
            user-related database operations

        """
        return self._dao

    async def get_user_by_id(self, user_id: uuid.UUID | str) -> User:
        """Retrieve a user by their ID from the database.

        Args:
            user_id (uuid.UUID): The unique identifier of the user to retrieve

        Returns:
            User: The user object if found

        Raises:
            UserNotFoundByIdException: If no active user
            is found with the given ID

        """
        async with self.session.begin():
            user: User | None = await self.dao.get_one(id=user_id)
        if not user:
            raise UserNotFoundByIdException
        return user

    async def create_new_user(
        self,
        user: CreateUserRequestSchema,
    ) -> User:
        """Create a new user in the database.

        Args:
            user (CreateUserRequestSchema): User data containing
            name, surname, email, password, and optional roles

        Returns:
            CreateUserResponseShema: Created user information including
            ID, name, surname, email, active status, and roles

        Note:
            If roles are not provided, defaults to [UserRoles.USER]

        """
        user_data = user.model_dump()
        user_secret_pass = user_data['password'].get_secret_value()
        user_data['password'] = Hasher.hash_password(user_secret_pass)
        async with self.session.begin():
            created_user: User = await self.dao.create(user_data)
        return created_user

    async def deactivate_user(self, target_user: User) -> None:
        """Deactivate a user in the database.

        Args:
            target_user (User): The user to be deactivated

        Returns:
            DeleteUserResponseSchema: Response with the deactivated user ID

        Raises:
            UserNotFoundByIdException: If the target user is not found

        Note:
            This operation sets the user's is_active flag to False

        """
        async with self.dao.session.begin():
            deleted_user: User | None = await self.dao.update(
                self._DEACTIVATE_USER_UPDATE, id=target_user.id
            )
        if not deleted_user:
            raise UserNotFoundByIdException

    async def update_user(
        self,
        target_user: User,
        user_fields: UpdateUserRequestSchema,
    ) -> User:
        """Update user information in the database.

        Args:
            target_user (User): The user whose information will be updated
            user_fields (UpdateUserRequestSchema): Schema containing
             the fields to update

        Returns:
            UpdateUserResponseSchema: Response containing the updated user

        Raises:
            ForgottenParametersException: If no fields are provided for update
            UserNotFoundByIdException: If the target user is not found

        Note:
            Only non-null fields from the request schema will be updated

        """
        filtered_user_fields: dict[str, str] = (
            self._validate_schema_for_update_request(user_fields)
        )
        async with self.session.begin():
            updated_user: User | None = await self.dao.update(
                filtered_user_fields, id=target_user.id
            )
        if not updated_user:
            raise UserNotFoundByIdException
        return updated_user

    async def set_admin_privilege(
        self,
        target_user: User,
    ) -> User:
        """Grant admin privileges to a user.

        Args:
            target_user (User): The user to whom admin
             privileges will be granted

        Returns:
            UpdateUserResponseSchema: Response containing the ID-updated user.

        Raises:
            UserNotFoundByIdException: If the target user is not found

        Note:
            This operation adds the ADMIN role to the user's roles list

        """
        async with self.session.begin():
            updated_user: User | None = await self.dao.update(
                self._SET_ADMIN_UPDATE, id=target_user.id
            )
        if not updated_user:
            raise UserNotFoundByIdException
        return updated_user

    async def revoke_admin_privilege(
        self,
        target_user: User,
    ) -> User:
        """Revoke admin privileges from a user.

        Args:
            target_user (User): The user from whom to revoke admin privileges

        Returns:
            UpdateUserResponseSchema: Response containing the ID-updated user.

        Raises:
            UserNotFoundByIdException: If the target user is not found

        Note:
            This operation removes the ADMIN role from the user's roles list

        """
        async with self.session.begin():
            updated_user: User | None = await self.dao.update(
                self._REVOKE_ADMIN_UPDATE, target_user.id
            )
        if not updated_user:
            raise UserNotFoundByIdException
        return updated_user
