import uuid
from typing import Optional

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
    UserQueryIdMissmatchException,
    UserNotFoundByIdException,
    ForgottenParametersException,
)
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    @staticmethod
    def _validate_jwt_query_id(
        query_uuid: uuid.UUID, jwt_uuid: uuid.UUID
    ) -> None:
        """
        Validate uuid from jwt the same as uuid from query

        :param query_uuid: uuid from query
        :param jwt_uuid: uuid from jwt token
        """
        if query_uuid != jwt_uuid:
            raise UserQueryIdMissmatchException

    @classmethod
    async def create_new_user(
        cls, user: CreateUser, db: AsyncSession
    ) -> ShowUser:
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
        jwt_user_id: uuid.UUID,
        db: AsyncSession,
    ) -> DeleteUserResponse:
        cls._validate_jwt_query_id(requested_user_id, jwt_user_id)
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_id(
                    user_id=requested_user_id
                )
                if not user:
                    raise UserNotFoundByIdException
                deleted_user_id: Optional[
                    uuid.UUID
                ] = await user_dal.deactivate_user(requested_user_id)
        if not deleted_user_id:
            raise UserNotFoundByIdException
        return DeleteUserResponse(deleted_user_id=deleted_user_id)

    @classmethod
    async def get_user(
        cls,
        requested_user_id: uuid.UUID,
        jwt_user_id: uuid.UUID,
        db: AsyncSession,
    ) -> ShowUser:
        cls._validate_jwt_query_id(requested_user_id, jwt_user_id)
        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_id(
                    requested_user_id
                )
        if not user:
            raise UserNotFoundByIdException
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
            user_roles=user.roles,
        )

    @classmethod
    async def update_user(
        cls,
        requested_user_id: uuid.UUID,
        jwt_user_id: uuid.UUID,
        user_fields: UpdateUserRequest,
        db: AsyncSession,
    ) -> UpdateUserResponse:
        cls._validate_jwt_query_id(requested_user_id, jwt_user_id)

        filtered_user_fields: dict[str, str] = user_fields.model_dump(
            exclude_none=True
        )  # Delete None key value pair
        if not filtered_user_fields:
            raise ForgottenParametersException

        async with db as session:
            async with session.begin():
                user_dal = UserDAL(session)
                user: Optional[User] = await user_dal.get_user_by_id(
                    requested_user_id
                )
                if not user:
                    raise UserNotFoundByIdException
                updated_user_id: Optional[
                    uuid.UUID
                ] = await user_dal.update_user(
                    requested_user_id,
                    **filtered_user_fields,
                )
        if not updated_user_id:
            raise UserNotFoundByIdException

        return UpdateUserResponse(updated_user_id=updated_user_id)
