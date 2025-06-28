import uuid
from typing import Optional

from sqlalchemy.exc import IntegrityError

from src.users.models import User
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.schemas import CreateUser, UpdateUserRequest
from src.users.dal import UserDAL


class TestUserDAL:
    @staticmethod
    async def _base_revoke_admin_privilege(
        user_id: uuid.UUID, session: AsyncSession
    ) -> Optional[uuid.UUID]:
        user_dal = UserDAL(session)
        return await user_dal.revoke_admin_privilege(target_user_id=user_id)

    @staticmethod
    async def _base_set_admin_privilege(
        user_id: uuid.UUID, session: AsyncSession
    ) -> Optional[uuid.UUID]:
        user_dal = UserDAL(session)
        return await user_dal.set_admin_privilege(target_user_id=user_id)

    @staticmethod
    async def _base_user_update(
        user_id: uuid.UUID,
        updated_user: UpdateUserRequest,
        session: AsyncSession,
    ) -> Optional[uuid.UUID]:
        filtered_user_fields: dict[str, str] = updated_user.model_dump()
        user_dal = UserDAL(session)
        return await user_dal.update_user(user_id, **filtered_user_fields)

    @staticmethod
    async def _base_user_create(
        test_schema: CreateUser, session: AsyncSession
    ) -> User:
        user_dal = UserDAL(session)
        return await user_dal.create_user(
            name=test_schema.name,
            surname=test_schema.surname,
            email=test_schema.email,
            password=test_schema.password,
            user_roles=test_schema.user_roles,  # type: ignore
        )

    @staticmethod
    async def _base_user_deactivate(
        user_id: uuid.UUID, session: AsyncSession
    ) -> Optional[uuid.UUID]:
        user_dal = UserDAL(session)
        return await user_dal.deactivate_user(user_id)

    @staticmethod
    async def _base_user_get_by_id(
        user_id: uuid.UUID, session: AsyncSession
    ) -> Optional[User]:
        user_dal = UserDAL(session)
        return await user_dal.get_user_by_id(user_id)

    @staticmethod
    async def _base_user_get_by_email(
        email: str, session: AsyncSession
    ) -> Optional[User]:
        user_dal = UserDAL(session)
        return await user_dal.get_user_by_email(email)

    @staticmethod
    def _base_user_assert(user: User, test_user_schema: CreateUser) -> None:
        assert user
        assert user.name == test_user_schema.name
        assert user.surname == test_user_schema.surname
        assert user.email == test_user_schema.email
        assert user.password == test_user_schema.password
        assert user.is_active
        assert user.roles == test_user_schema.user_roles

    @staticmethod
    def _base_updated_user_assert(
        user: User,
        test_user_schema: CreateUser,
        updated_user_schema: UpdateUserRequest,
    ) -> None:
        assert updated_user_schema.name == user.name
        assert test_user_schema.name != user.name
        assert updated_user_schema.surname == user.surname
        assert test_user_schema.surname != user.surname
        assert updated_user_schema.email == user.email
        assert test_user_schema.email != user.email

    @pytest.mark.asyncio
    async def test_create_user(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)

    @pytest.mark.asyncio
    async def test_create_user_duplicated_user(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        with pytest.raises(IntegrityError):
            for _ in range(2):
                user = await self._base_user_create(
                    test_user_schema, db_session
                )
                self._base_user_assert(user, test_user_schema)
        assert True

    @pytest.mark.asyncio
    async def test_deactivate_user(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)
        deactivated_user_id = await self._base_user_deactivate(
            user.user_id, db_session
        )
        assert deactivated_user_id == user.user_id
        assert not user.is_active

    @pytest.mark.asyncio
    async def test_deactivate_inactive_user(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)
        deactivated_user_id = await self._base_user_deactivate(
            user.user_id, db_session
        )
        assert deactivated_user_id
        deactivated_again_user_id = await self._base_user_deactivate(
            deactivated_user_id, db_session
        )
        assert not deactivated_again_user_id

    @pytest.mark.asyncio
    async def test_get_user_by_id(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)
        get_user = await self._base_user_get_by_id(user.user_id, db_session)
        assert get_user
        self._base_user_assert(get_user, test_user_schema)

    @pytest.mark.asyncio
    async def test_get_user_by_wrong_id(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        random_uid = uuid.uuid4()
        get_user = await self._base_user_get_by_id(random_uid, db_session)
        assert not get_user

    @pytest.mark.asyncio
    async def test_get_user_by_email(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)
        get_user = await self._base_user_get_by_email(user.email, db_session)
        assert get_user
        self._base_user_assert(get_user, test_user_schema)

    @pytest.mark.asyncio
    async def test_get_user_by_wrong_email(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        random_email = "test-none@gmail.com"
        get_user = await self._base_user_get_by_email(random_email, db_session)
        assert not get_user

    @pytest.mark.asyncio
    async def test_update_user(
        self,
        test_user_schema: CreateUser,
        update_user_schema: UpdateUserRequest,
        db_session: AsyncSession,
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)
        updated_user_id = await self._base_user_update(
            user.user_id, update_user_schema, db_session
        )
        assert updated_user_id == user.user_id
        updated_user = await self._base_user_get_by_id(
            updated_user_id, db_session
        )
        assert updated_user
        self._base_updated_user_assert(
            user, test_user_schema, update_user_schema
        )

    @pytest.mark.asyncio
    async def test_update_user_with_none_email(
        self,
        test_user_schema: CreateUser,
        update_user_schema: UpdateUserRequest,
        db_session: AsyncSession,
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        assert user
        self._base_user_assert(user, test_user_schema)
        update_user_schema.email = None
        with pytest.raises(IntegrityError):
            await self._base_user_update(
                user.user_id, update_user_schema, db_session
            )
        assert True

    @pytest.mark.asyncio
    async def test_update_user_with_none_surname_name(
        self,
        test_user_schema: CreateUser,
        update_user_schema: UpdateUserRequest,
        db_session: AsyncSession,
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)
        update_user_schema.name = None
        update_user_schema.surname = None
        with pytest.raises(IntegrityError):
            await self._base_user_update(
                user.user_id, update_user_schema, db_session
            )
        assert True

    @pytest.mark.asyncio
    async def test_set_admin_privilege(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)
        updated_user_id = await self._base_set_admin_privilege(
            user.user_id, db_session
        )
        assert updated_user_id == user.user_id
        admin_user = await self._base_user_get_by_id(
            updated_user_id, db_session
        )
        assert admin_user
        assert admin_user.name == test_user_schema.name
        assert admin_user.surname == test_user_schema.surname
        assert admin_user.email == test_user_schema.email
        assert admin_user.password == test_user_schema.password
        assert admin_user.roles != test_user_schema.user_roles
        assert "admin" in admin_user.roles

    @pytest.mark.asyncio
    async def test_revoke_admin_privilege(
        self, test_user_schema: CreateUser, db_session: AsyncSession
    ) -> None:
        user = await self._base_user_create(test_user_schema, db_session)
        self._base_user_assert(user, test_user_schema)
        updated_user_id = await self._base_set_admin_privilege(
            user.user_id, db_session
        )
        assert updated_user_id == user.user_id
        admin_user = await self._base_user_get_by_id(
            updated_user_id, db_session
        )
        assert admin_user
        assert admin_user.roles != test_user_schema.user_roles
        assert "admin" in admin_user.roles
        revoked_user_id = await self._base_revoke_admin_privilege(
            admin_user.user_id, db_session
        )
        assert revoked_user_id
        revoked_user = await self._base_user_get_by_id(
            revoked_user_id, db_session
        )
        assert revoked_user
        assert revoked_user.user_id == admin_user.user_id
        assert revoked_user.roles == test_user_schema.user_roles
        assert "admin" not in admin_user.roles
