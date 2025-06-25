import uuid
from typing import Optional

from src.auth.enums import UserAction
from src.auth.services import PermissionService
from src.users.dal import UserDAL
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
    @staticmethod
    async def _fetch_user_with_validation(
        requested_user_id: uuid.UUID,
        current_user: User,
        db: AsyncSession,
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

        async with db as session:
            async with session.begin():
                user_dal: UserDAL = UserDAL(session)
                target_user: Optional[User] = await user_dal.get_user_by_id(
                    user_id=requested_user_id
                )
        if not target_user:
            raise UserNotFoundByIdException
        PermissionService.validate_permission(target_user, current_user, action)
        return target_user

    @classmethod
    async def create_new_user(
        cls, user: CreateUser, db: AsyncSession
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

        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                created_user: User = await user_dal.create_user(
                    name=user.name,
                    surname=user.surname,
                    email=user.email,
                    password=Hasher.hash_password(user.password),
                    user_roles=user.user_roles
                    if user.user_roles
                    else [UserRoles.USER],  # noqa: F821
                )
                return ShowUser(
                    user_id=created_user.user_id,
                    name=created_user.name,
                    surname=created_user.surname,
                    email=created_user.email,
                    is_active=created_user.is_active,
                    user_roles=created_user.roles,
                )

    @classmethod
    async def deactivate_user(
        cls,
        requested_user_id: uuid.UUID,
        jwt_user_id: User,
        db: AsyncSession,
    ) -> DeleteUserResponse:
        target_user: User = await cls._fetch_user_with_validation(
            requested_user_id, jwt_user_id, db, UserAction.DELETE
        )
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                deleted_user_id: Optional[
                    uuid.UUID
                ] = await user_dal.deactivate_user(target_user.user_id)
        if not deleted_user_id:
            raise UserNotFoundByIdException
        return DeleteUserResponse(deleted_user_id=deleted_user_id)

    @classmethod
    async def get_user(
        cls,
        requested_user_id: uuid.UUID,
        jwt_user_id: User,
        db: AsyncSession,
    ) -> ShowUser:
        target_user = await cls._fetch_user_with_validation(
            requested_user_id, jwt_user_id, db, UserAction.GET
        )
        return ShowUser(
            user_id=target_user.user_id,
            name=target_user.name,
            surname=target_user.surname,
            email=target_user.email,
            is_active=target_user.is_active,
            user_roles=target_user.roles,
        )

    @classmethod
    async def update_user(
        cls,
        requested_user_id: uuid.UUID,
        jwt_user_id: User,
        user_fields: UpdateUserRequest,
        db: AsyncSession,
    ) -> UpdateUserResponse:
        filtered_user_fields: dict[str, str] = user_fields.model_dump(
            exclude_none=True
        )  # Delete None key value pair
        if not filtered_user_fields:
            raise ForgottenParametersException
        target_user: User = await cls._fetch_user_with_validation(
            requested_user_id, jwt_user_id, db, UserAction.UPDATE
        )
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                updated_user_id: Optional[
                    uuid.UUID
                ] = await user_dal.update_user(
                    target_user.user_id,
                    **filtered_user_fields,
                )
        if not updated_user_id:
            raise UserNotFoundByIdException
        return UpdateUserResponse(updated_user_id=updated_user_id)

    @classmethod
    async def set_admin_privilege(
        cls,
        jwt_user: User,
        requested_user_id: uuid.UUID,
        db: AsyncSession,
    ) -> UpdateUserResponse:
        target_user = await cls._fetch_user_with_validation(
            requested_user_id, jwt_user, db, UserAction.SET_ADMIN_PRIVILEGE
        )
        async with db as session:
            async with session.begin():
                user_dal: UserDAL = UserDAL(session)
                updated_user_id: Optional[
                    uuid.UUID
                ] = await user_dal.set_admin_privilege(target_user.user_id)
                if not updated_user_id:
                    raise UserNotFoundByIdException
                return UpdateUserResponse(updated_user_id=updated_user_id)
