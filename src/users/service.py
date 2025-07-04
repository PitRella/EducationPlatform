import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.hashing import Hasher
from src.users.dao import UserDAO
from src.users.enums import UserRoles
from src.users.exceptions import (
    ForgottenParametersException,
    UserNotFoundByIdException,
)
from src.users.models import User
from src.users.schemas import (
    CreateUser,
    DeleteUserResponse,
    ShowUser,
    UpdateUserRequest,
    UpdateUserResponse,
)


class UserService:
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
        self._session: AsyncSession = db_session
        self._dao: UserDAO = dao or UserDAO(db_session)

    @property
    def dao(self) -> UserDAO:
        """Get the data access object associated with this service.

        Returns:
            UserDAO: The Data Access Object for
            user-related database operations

        """
        return self._dao

    @property
    def session(self) -> AsyncSession:
        """Get the database session associated with this service.

        Returns:
            AsyncSession: The SQLAlchemy async session for database operations

        """
        return self._session

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
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
            user: User | None = await self.dao.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundByIdException
        return user

    async def create_new_user(
        self,
        user: CreateUser,
    ) -> ShowUser:
        """Create a new user in the database.

        Args:
            user (CreateUser): User data containing
            name, surname, email, password, and optional roles

        Returns:
            ShowUser: Created user information including
            ID, name, surname, email, active status, and roles

        Note:
            If user_roles are not provided, defaults to [UserRoles.USER]

        """
        async with self.session.begin():
            created_user: User = await self.dao.create_user(
                name=user.name,
                surname=user.surname,
                email=user.email,
                password=Hasher.hash_password(user.password),
                user_roles=user.user_roles
                if user.user_roles
                else [UserRoles.USER],
            )
        return ShowUser.model_validate(created_user)

    async def deactivate_user(self, target_user: User) -> DeleteUserResponse:
        """Deactivate a user in the system.

        Args:
            target_user (User): The user to be deactivated

        Returns:
            DeleteUserResponse: Response containing the
             ID of the deactivated user

        Raises:
            UserNotFoundByIdException: If the target user is not found

        Note:
            This operation sets the user's is_active flag to False

        """
        async with self.session.begin():
            deleted_user_id: uuid.UUID | None = await self.dao.deactivate_user(
                target_user.user_id,
            )
        if not deleted_user_id:
            raise UserNotFoundByIdException
        return DeleteUserResponse(deleted_user_id=deleted_user_id)

    async def update_user(
        self,
        target_user: User,
        user_fields: UpdateUserRequest,
    ) -> UpdateUserResponse:
        """Update user information in the database.

        Args:
            target_user (User): The user object to be updated
            user_fields (UpdateUserRequest): Fields to update
            containing optional name, surname, email

        Returns:
            UpdateUserResponse: Response containing the ID of the updated user

        Raises:
            ForgottenParametersException: If no fields are provided for update
            UserNotFoundByIdException: If the target user is not found

        Note:
            Only non-None fields from user_fields will be used for the update

        """
        filtered_user_fields: dict[str, str] = user_fields.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )  # Delete None key value pair
        if not filtered_user_fields:
            raise ForgottenParametersException
        async with self.session.begin():
            updated_user_id: uuid.UUID | None = await self.dao.update_user(
                target_user.user_id,
                **filtered_user_fields,
            )
        if not updated_user_id:
            raise UserNotFoundByIdException
        return UpdateUserResponse(updated_user_id=updated_user_id)

    async def set_admin_privilege(
        self,
        target_user: User,
    ) -> UpdateUserResponse:
        """Grant admin privileges to a user.

        Args:
            target_user (User): The user to whom admin
             privileges will be granted

        Returns:
            UpdateUserResponse: Response containing the ID of the updated user

        Raises:
            UserNotFoundByIdException: If the target user is not found

        Note:
            This operation adds the ADMIN role to the user's roles list

        """
        async with self.session.begin():
            updated_user_id: (
                uuid.UUID | None
            ) = await self.dao.set_admin_privilege(target_user.user_id)
        if not updated_user_id:
            raise UserNotFoundByIdException
        return UpdateUserResponse(updated_user_id=updated_user_id)

    async def revoke_admin_privilege(
        self,
        target_user: User,
    ) -> UpdateUserResponse:
        """Revoke admin privileges from a user.

        Args:
            target_user (User): The user from whom to revoke admin privileges

        Returns:
            UpdateUserResponse: Response containing the ID of the updated user

        Raises:
            UserNotFoundByIdException: If the target user is not found

        Note:
            This operation removes the ADMIN role from the user's roles list

        """
        async with self.session.begin():
            updated_user_id: (
                uuid.UUID | None
            ) = await self.dao.revoke_admin_privilege(target_user.user_id)
        if not updated_user_id:
            raise UserNotFoundByIdException
        return UpdateUserResponse(updated_user_id=updated_user_id)
