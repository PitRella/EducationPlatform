import uuid
from typing import Optional

from src.auth.enums import UserAction
from src.auth.services import PermissionService
from src.users.dao import UserDAO
from src.hashing import Hasher
from src.users.models import User
from src.users.enums import UserRoles
from src.users.schemas import (
    CreateUser,
    ShowUser,
    UpdateUserResponse,
    UpdateUserRequest,
    DeleteUserResponse,
)
from src.users.exceptions import (
    UserNotFoundByIdException,
    ForgottenParametersException,
)
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(
        self, db_session: AsyncSession, dao: Optional[UserDAO] = None
    ) -> None:
        self._session: AsyncSession = db_session
        self._dao: UserDAO = dao or UserDAO(db_session)

    @property
    def dao(self) -> UserDAO:
        return self._dao

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def _fetch_user_with_validation(
        self,
        requested_user_id: uuid.UUID,
        current_user: User,
        action: UserAction,
    ) -> User:
        """
        Retrieve and validate user permissions between the requested and current user.

        Args:
            requested_user_id (uuid.UUID): ID of the user being requested/targeted
            current_user (uuid.UUID): User making the request (from JWT token)
            db (AsyncSession): Database session for transaction management
            action (UserAction): User action to perform

        Returns:
            User: The target user object if validation succeeds

        Raises:
            UserNotFoundByIdException: If either target or current user is not found,
            PermissionException: If the current user lacks permission to access the target user
        """
        async with self.session.begin():
            target_user: Optional[User] = await self.dao.get_user_by_id(
                user_id=requested_user_id
            )
        if not target_user:
            raise UserNotFoundByIdException
        PermissionService.validate_permission(target_user, current_user, action)
        return target_user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        async with self.session.begin():
            user: Optional[User] = await self.dao.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundByIdException
        return user

    async def create_new_user(
        self,
        user: CreateUser,
    ) -> ShowUser:
        """
        Create a new user in the database.

        Args:
            user (CreateUser): User data containing name, surname, email, password and optional roles
            db (AsyncSession): Database session for transaction management

        Returns:
            ShowUser: Created user information including ID, name, surname, email, active status and roles

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
                else [UserRoles.USER],  # noqa: F821
            )
            return ShowUser.model_validate(created_user)

    async def deactivate_user(self, target_user: User) -> DeleteUserResponse:
        async with self.session.begin():
            deleted_user_id: Optional[
                uuid.UUID
            ] = await self.dao.deactivate_user(target_user.user_id)
        if not deleted_user_id:
            raise UserNotFoundByIdException
        return DeleteUserResponse(deleted_user_id=deleted_user_id)

    async def get_user(
        self,
        requested_user_id: uuid.UUID,
        jwt_user: User,
    ) -> ShowUser:
        target_user = await self._fetch_user_with_validation(
            requested_user_id, jwt_user, UserAction.GET
        )
        return ShowUser.model_validate(target_user)

    async def update_user(
        self,
        target_user: User,
        user_fields: UpdateUserRequest,
    ) -> UpdateUserResponse:
        filtered_user_fields: dict[str, str] = user_fields.model_dump(
            exclude_none=True, exclude_unset=True
        )  # Delete None key value pair
        if not filtered_user_fields:
            raise ForgottenParametersException
        async with self.session.begin():
            updated_user_id: Optional[uuid.UUID] = await self.dao.update_user(
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
        async with self.session.begin():
            updated_user_id: Optional[
                uuid.UUID
            ] = await self.dao.set_admin_privilege(target_user.user_id)
        if not updated_user_id:
            raise UserNotFoundByIdException
        return UpdateUserResponse(updated_user_id=updated_user_id)

    async def revoke_admin_privilege(
        self,
        target_user: User,
    ) -> UpdateUserResponse:
        async with self.session.begin():
            updated_user_id: Optional[
                uuid.UUID
            ] = await self.dao.revoke_admin_privilege(target_user.user_id)
        if not updated_user_id:
            raise UserNotFoundByIdException
        return UpdateUserResponse(updated_user_id=updated_user_id)
