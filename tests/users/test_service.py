import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.enums import UserAction
from src.auth.exceptions import PermissionException
from src.users.enums import UserRoles
from src.users.exceptions import (
    ForgottenParametersException,
    UserNotFoundByIdException,
)
from src.users.models import User
from src.users.schemas import CreateUser, UpdateUserRequest
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
        for k, v in kwargs.items():
            setattr(self._user, k, v)
        return self._user.user_id

    async def deactivate_user(  # type: ignore
        self, *args, **kwargs
    ) -> uuid.UUID:
        return await self.update_user(*args, **kwargs)

    async def set_admin_privilege(  # type: ignore
        self, *args, **kwargs
    ) -> uuid.UUID:
        return await self.update_user(*args, roles=[UserRoles.ADMIN])

    async def revoke_admin_privilege(  # type: ignore
        self, *args, **kwargs
    ) -> uuid.UUID:
        return await self.update_user(*args, roles=[UserRoles.USER])


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
        """Test create user with superadmin roles."""
        user_schema.user_roles = [UserRoles.SUPERADMIN]
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(superadmin_user_obj),  # type: ignore
        )
        await service.create_new_user(user_schema)
        assert superadmin_user_obj.roles == ["superadmin"]

    @pytest.mark.asyncio
    async def test_update_user(
        self,
        db_session: AsyncSession,
        update_user_schema: UpdateUserRequest,
        default_user_obj: User,
    ) -> None:
        """Test to user update his own profile"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.update_user(
            default_user_obj.user_id, default_user_obj, update_user_schema
        )
        updated_user = await service.get_user(
            default_user_obj.user_id, default_user_obj
        )
        assert updated_user.user_id == default_user_obj.user_id
        assert updated_user.name == update_user_schema.name
        assert updated_user.surname == update_user_schema.surname
        assert updated_user.email == update_user_schema.email

    @pytest.mark.asyncio
    async def test_update_user_email_none(
        self,
        db_session: AsyncSession,
        update_user_schema: UpdateUserRequest,
        default_user_obj: User,
    ) -> None:
        """Test to user update email to none"""
        update_user_schema.email = None
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.update_user(
            default_user_obj.user_id, default_user_obj, update_user_schema
        )
        updated_user = await service.get_user(
            default_user_obj.user_id, default_user_obj
        )
        assert updated_user.user_id == default_user_obj.user_id
        assert updated_user.name == update_user_schema.name
        assert updated_user.surname == update_user_schema.surname
        # Email should not be changed, because it is None
        assert updated_user.email == default_user_obj.email

    @pytest.mark.asyncio
    async def test_update_user_all_fields_none(
        self,
        db_session: AsyncSession,
        update_user_schema: UpdateUserRequest,
        default_user_obj: User,
    ) -> None:
        """Test to user update every field with none"""
        update_user_schema.name = None
        update_user_schema.surname = None
        update_user_schema.email = None
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        # All fields should not be changed because it is None
        with pytest.raises(ForgottenParametersException):
            await service.update_user(
                default_user_obj.user_id, default_user_obj, update_user_schema
            )
        assert True

    @pytest.mark.asyncio
    async def test_deactivate_inactive_regular_user(
        self,
        db_session: AsyncSession,
        superadmin_user_obj: User,
        default_user_obj: User,
    ) -> None:
        """Test to deactivate an inactive user"""
        default_user_obj.is_active = False
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        with pytest.raises(UserNotFoundByIdException):
            await service.deactivate_user(
                default_user_obj.user_id, default_user_obj
            )

    @pytest.mark.asyncio
    async def test_deactivate_regular_user(
        self,
        db_session: AsyncSession,
        superadmin_user_obj: User,
        default_user_obj: User,
    ) -> None:
        """Test to deactivate an inactive user"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        deactivated_user_schema = await service.deactivate_user(
            default_user_obj.user_id, default_user_obj
        )
        assert (
            deactivated_user_schema.deleted_user_id == default_user_obj.user_id
        )

    @pytest.mark.parametrize(
        "test_user", ["admin_user_obj", "superadmin_user_obj"], indirect=True
    )
    @pytest.mark.asyncio
    async def test_deactivate_admin_user(
        self,
        db_session: AsyncSession,
        test_user: User,
    ) -> None:
        """Test to deactivate an admin user"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(test_user),  # type: ignore
        )
        with pytest.raises(PermissionException):
            await service.deactivate_user(test_user.user_id, test_user)

    #
    @pytest.mark.parametrize(
        "test_user", ["admin_user_obj", "superadmin_user_obj"], indirect=True
    )
    @pytest.mark.asyncio
    async def test_deactivate_regular_user_by_superadmin(
        self,
        db_session: AsyncSession,
        default_user_obj: User,
        test_user: User,
    ) -> None:
        """Test to deactivate a regular user by admin user"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        await service.deactivate_user(default_user_obj.user_id, test_user)

    @pytest.mark.parametrize(
        "test_user",
        ["default_user_obj", "admin_user_obj", "superadmin_user_obj"],
        indirect=True,
    )
    @pytest.mark.asyncio
    async def test_set_admin_privilege_on_user_himself(
        self,
        db_session: AsyncSession,
        test_user: User,
    ) -> None:
        """Test user set admin privilege on himself"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(test_user),  # type: ignore
        )
        with pytest.raises(PermissionException):
            await service.set_admin_privilege(test_user, test_user.user_id)

    @pytest.mark.parametrize(
        "test_user", ["default_user_obj", "admin_user_obj"], indirect=True
    )
    @pytest.mark.asyncio
    async def test_set_admin_privilege_on_other_users(
        self,
        db_session: AsyncSession,
        test_user: User,
        superadmin_user_obj: User,
    ) -> None:
        """Test superadmin set admin privilege on another user"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(test_user),  # type: ignore
        )
        upd_user_schema = await service.set_admin_privilege(
            superadmin_user_obj, test_user.user_id
        )
        assert test_user.user_id == upd_user_schema.updated_user_id
        assert test_user.roles == ["admin"]

    @pytest.mark.asyncio
    async def test_revoke_admin_privilege(
        self,
        db_session: AsyncSession,
        superadmin_user_obj: User,
        default_user_obj: User,
    ) -> None:
        """Test superadmin revoke admin privilege from another user"""
        service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        upd_user_schema = await service.revoke_admin_privilege(
            superadmin_user_obj, superadmin_user_obj.user_id
        )
        assert default_user_obj.user_id == upd_user_schema.updated_user_id
        assert default_user_obj.roles == ["user"]
