import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.enums import UserAction
from src.auth.exceptions import PermissionException
from src.users.enums import UserRoles
from src.users.models import User
from src.users.schemas import CreateUser
from src.users.service import UserService


class MockUserDAO:
    def __init__(self, user_obj: User):
        self._user = user_obj

    async def create_user(self, *args, **kwargs) -> User:  # type: ignore
        return User(
            user_id=self._user.user_id,
            name=self._user.name,
            surname=self._user.surname,
            email=self._user.email,
            password=self._user.password,
            roles=self._user.roles,
            is_active=self._user.is_active,
        )

    async def get_user_by_id(self, *args, **kwargs) -> User:  # type: ignore
        return await self.create_user()

    async def get_user_by_email(self, *args, **kwargs) -> User:  # type: ignore
        return await self.create_user()

    async def update_user(self, *args, **kwargs) -> uuid.UUID:  # type: ignore
        return self._user.user_id

    async def deactivate_user(  # type: ignore
        self, *args, **kwargs
    ) -> uuid.UUID:
        return self._user.user_id

    async def set_admin_privilege(  # type: ignore
        self, *args, **kwargs
    ) -> uuid.UUID:
        return self._user.user_id

    async def revoke_admin_privilege(  # type: ignore
        self, *args, **kwargs
    ) -> uuid.UUID:
        return self._user.user_id


class TestUserService:
    async def _base_user_assert(
        self, result_user: User, original_user: User
    ) -> None:
        assert result_user
        assert result_user.user_id == original_user.user_id
        assert result_user.name == original_user.name
        assert result_user.surname == original_user.surname
        assert result_user.email == original_user.email
        assert result_user.roles == original_user.roles
        assert result_user.is_active == original_user.is_active

    @pytest.mark.parametrize("action", list(UserAction))
    @pytest.mark.asyncio
    async def test_fetch_user_operations_on_himself(
        self,
        db_session: AsyncSession,
        default_user_obj: User,
        action: UserAction,
    ) -> None:
        """Test regular user for default user actions"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        if action in (  # Default user cannot modify an admin role on himself
            UserAction.SET_ADMIN_PRIVILEGE,
            UserAction.REVOKE_ADMIN_PRIVILEGE,
        ):
            with pytest.raises(PermissionException):
                await service._fetch_user_with_validation(
                    default_user_obj.user_id, default_user_obj, action
                )
            assert True
        else:  # Another action performs as usual
            result_user = await service._fetch_user_with_validation(
                default_user_obj.user_id, default_user_obj, action
            )
            await self._base_user_assert(result_user, default_user_obj)

    @pytest.mark.parametrize("action", list(UserAction))
    @pytest.mark.asyncio
    async def test_fetch_user_operations_on_another_user(
        self,
        db_session: AsyncSession,
        default_user_obj: User,
        admin_user_obj: User,  # noqa: F811
        action: UserAction,
    ) -> None:
        """Test to see a user make any action on another user"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(admin_user_obj),  # type: ignore
        )
        with pytest.raises(PermissionException):
            await service._fetch_user_with_validation(
                requested_user_id=admin_user_obj.user_id,
                current_user=default_user_obj,
                action=action,
            )
        assert True

    @pytest.mark.parametrize(
        "test_user", ["admin_user_obj", "superadmin_user_obj"], indirect=True
    )
    @pytest.mark.parametrize("action", list(UserAction))
    @pytest.mark.asyncio
    async def test_fetch_admins_operations_on_himself(
        self, db_session: AsyncSession, test_user: User, action: UserAction
    ) -> None:
        """
        Test to make sure superadmin/admin cannot
        delete, revoke/give admin priveleges on himself
        """
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(test_user),  # type: ignore
        )
        if action in (
            UserAction.DELETE,
            UserAction.SET_ADMIN_PRIVILEGE,
            UserAction.REVOKE_ADMIN_PRIVILEGE,
        ):
            with pytest.raises(PermissionException):
                await service._fetch_user_with_validation(
                    test_user.user_id, test_user, action
                )
            assert True
        else:
            result_user = await service._fetch_user_with_validation(
                requested_user_id=test_user.user_id,
                current_user=test_user,
                action=action,
            )
            await self._base_user_assert(result_user, test_user)

    @pytest.mark.asyncio
    async def test_get_user(
        self, db_session: AsyncSession, default_user_obj: User
    ) -> None:
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        show_user = await service.get_user(
            default_user_obj.user_id, default_user_obj
        )
        assert show_user
        assert show_user.user_id == default_user_obj.user_id
        assert show_user.name == default_user_obj.name
        assert show_user.surname == default_user_obj.surname
        assert show_user.email == default_user_obj.email
        assert show_user.is_active == default_user_obj.is_active
        assert show_user.user_roles == default_user_obj.roles

    @pytest.mark.asyncio
    async def test_create_new_user_with_none_roles(
        self,
        db_session: AsyncSession,
        user_schema: CreateUser,
        default_user_obj: User,
    ) -> None:
        """Test create user if roles are none."""
        user_schema.user_roles = None
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert default_user_obj.roles == ["user"]

    @pytest.mark.asyncio
    async def test_create_new_user_with_regular_roles(
        self,
        db_session: AsyncSession,
        user_schema: CreateUser,
        default_user_obj: User,
    ) -> None:
        """Test create user with user roles."""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert default_user_obj.roles == ["user"]

    @pytest.mark.asyncio
    async def test_create_new_user_with_admin_roles(
        self,
        db_session: AsyncSession,
        user_schema: CreateUser,
        admin_user_obj: User,
    ) -> None:
        """Test create user with admin roles."""
        user_schema.user_roles = [UserRoles.ADMIN]
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(admin_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert admin_user_obj.roles == ["admin"]

    @pytest.mark.asyncio
    async def test_create_new_user_with_superadmin_roles(
        self,
        db_session: AsyncSession,
        user_schema: CreateUser,
        superadmin_user_obj: User,
    ) -> None:
        user_schema.user_roles = [UserRoles.SUPERADMIN]
        """Test create user with superadmin roles."""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(superadmin_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert superadmin_user_obj.roles == ["superadmin"]
