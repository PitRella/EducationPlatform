import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.enums import UserRoles
from src.users.exceptions import (
    ForgottenParametersException,
)
from src.users.models import User
from src.users.schemas import CreateUserRequestSchema, UpdateUserRequestSchema
from src.users.service import UserService
from tests.conftest import MockUserDAO


class TestUserService:
    async def _base_user_assert(
        self, result_user: User, original_user: User
    ) -> None:
        assert result_user
        assert result_user.id == original_user.id
        assert result_user.name == original_user.name
        assert result_user.surname == original_user.surname
        assert result_user.email == original_user.email
        assert result_user.roles == original_user.roles
        assert result_user.is_active == original_user.is_active

    @pytest.mark.asyncio
    async def test_create_new_user_with_none_roles(
        self,
        db_session: AsyncSession,
        user_schema: CreateUserRequestSchema,
        default_user_obj: User,
    ) -> None:
        """Test create user if roles are none."""
        user_schema.roles = None
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert default_user_obj.roles == ['user']

    @pytest.mark.asyncio
    async def test_create_new_user_with_regular_roles(
        self,
        db_session: AsyncSession,
        user_schema: CreateUserRequestSchema,
        default_user_obj: User,
    ) -> None:
        """Test create user with user roles."""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert default_user_obj.roles == ['user']

    @pytest.mark.asyncio
    async def test_create_new_user_with_admin_roles(
        self,
        db_session: AsyncSession,
        user_schema: CreateUserRequestSchema,
        admin_user_obj: User,
    ) -> None:
        """Test create user with admin roles."""
        user_schema.roles = [UserRoles.ADMIN]
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(admin_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert admin_user_obj.roles == ['admin']

    @pytest.mark.asyncio
    async def test_create_new_user_with_superadmin_roles(
        self,
        db_session: AsyncSession,
        user_schema: CreateUserRequestSchema,
        superadmin_user_obj: User,
    ) -> None:
        """Test create user with superadmin roles."""
        user_schema.roles = [UserRoles.SUPERADMIN]
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(superadmin_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert superadmin_user_obj.roles == ['superadmin']

    @pytest.mark.asyncio
    async def test_update_user(
        self,
        db_session: AsyncSession,
        update_user_schema: UpdateUserRequestSchema,
        default_user_obj: User,
    ) -> None:
        """Test to user update his own profile."""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.update_user(default_user_obj, update_user_schema)
        updated_user = await service.get_user(default_user_obj.id)  # type: ignore
        assert updated_user.id == default_user_obj.id
        assert updated_user.name == update_user_schema.name
        assert updated_user.surname == update_user_schema.surname
        assert updated_user.email == update_user_schema.email

    @pytest.mark.asyncio
    async def test_update_user_email_none(
        self,
        db_session: AsyncSession,
        update_user_schema: UpdateUserRequestSchema,
        default_user_obj: User,
    ) -> None:
        """Test to user update email to none."""
        update_user_schema.email = None
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.update_user(default_user_obj, update_user_schema)
        updated_user = await service.get_user(default_user_obj.id)  # type: ignore
        assert updated_user.id == default_user_obj.id
        assert updated_user.name == update_user_schema.name
        assert updated_user.surname == update_user_schema.surname
        # Email should not be changed, because it is None
        assert updated_user.email == default_user_obj.email

    @pytest.mark.asyncio
    async def test_update_user_all_fields_none(
        self,
        db_session: AsyncSession,
        update_user_schema: UpdateUserRequestSchema,
        default_user_obj: User,
    ) -> None:
        """Test to user update every field with none."""
        update_user_schema.name = None
        update_user_schema.surname = None
        update_user_schema.email = None
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        # All fields should not be changed because it is None
        with pytest.raises(ForgottenParametersException):
            await service.update_user(default_user_obj, update_user_schema)
        assert True

    @pytest.mark.asyncio
    async def test_deactivate_regular_user(
        self,
        db_session: AsyncSession,
        superadmin_user_obj: User,
        default_user_obj: User,
    ) -> None:
        """Test to deactivate an inactive user."""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        deactivated_user_schema = await service.deactivate_user(
            default_user_obj
        )
        assert deactivated_user_schema.deleted_user_id == default_user_obj.id

    @pytest.mark.parametrize(
        'test_user', ['default_user_obj', 'admin_user_obj'], indirect=True
    )
    @pytest.mark.asyncio
    async def test_set_admin_privilege_on_other_users(
        self,
        db_session: AsyncSession,
        test_user: User,
        superadmin_user_obj: User,
    ) -> None:
        """Test superadmin set admin privilege on another user."""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(test_user),  # type: ignore
        )
        upd_user_schema = await service.set_admin_privilege(superadmin_user_obj)
        assert test_user.id == upd_user_schema.updated_user_id
        assert test_user.roles == ['admin']

    @pytest.mark.asyncio
    async def test_revoke_admin_privilege(
        self,
        db_session: AsyncSession,
        superadmin_user_obj: User,
        default_user_obj: User,
    ) -> None:
        """Test superadmin revoke admin privilege from another user."""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        upd_user_schema = await service.revoke_admin_privilege(
            superadmin_user_obj
        )
        assert default_user_obj.id == upd_user_schema.updated_user_id
        assert default_user_obj.roles == ['user']
