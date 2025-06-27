import uuid
from typing import Optional

from sqlalchemy.exc import IntegrityError

from src.users.models import User
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.schemas import CreateUser
from src.users.dal import UserDAL


async def _create_user(
    user: CreateUser, db_session: AsyncSession
) -> Optional[User]:
    user_dal: "UserDAL" = UserDAL(db_session)
    return await user_dal.create_user(
        name=user.name,
        surname=user.surname,
        email=user.email,
        password=user.password,
        user_roles=user.user_roles,  # type: ignore
    )


async def _get_user_by_id(
    user: User, db_session: AsyncSession
) -> Optional[User]:
    user_dal: "UserDAL" = UserDAL(db_session)
    return await user_dal.get_user_by_id(user.user_id)


@pytest.mark.asyncio
async def test_create_user(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    created_user: Optional[User] = await _create_user(get_user, db_session)
    assert created_user
    assert created_user.name == get_user.name
    assert created_user.surname == get_user.surname
    assert created_user.email == get_user.email
    assert created_user.password == get_user.password
    assert created_user.roles == get_user.user_roles


@pytest.mark.asyncio
async def test_create_duplicated_user(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    created_user: Optional[User] = await _create_user(get_user, db_session)
    assert created_user
    assert created_user.name == get_user.name
    assert created_user.surname == get_user.surname
    assert created_user.email == get_user.email
    with pytest.raises(IntegrityError):
        await _create_user(get_user, db_session)


@pytest.mark.asyncio
async def test_get_user_by_email(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    user_dal: "UserDAL" = UserDAL(db_session)
    created_user: Optional[User] = await _create_user(get_user, db_session)
    assert created_user
    user_get: Optional[User] = await user_dal.get_user_by_email(get_user.email)
    assert user_get
    assert user_get.name == created_user.name
    assert user_get.surname == created_user.surname
    assert user_get.email == created_user.email


@pytest.mark.asyncio
async def test_get_user_by_email_error(db_session: AsyncSession) -> None:
    user_dal: "UserDAL" = UserDAL(db_session)
    user_get: Optional[User] = await user_dal.get_user_by_email(
        "fake_mail@tmail.com"
    )
    assert not user_get


@pytest.mark.asyncio
async def test_get_user_by_id(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    user_dal: "UserDAL" = UserDAL(db_session)
    created_user: Optional[User] = await _create_user(get_user, db_session)
    assert created_user
    user_get: Optional[User] = await user_dal.get_user_by_id(
        created_user.user_id
    )
    assert user_get
    assert user_get.name == created_user.name
    assert user_get.surname == created_user.surname
    assert user_get.email == created_user.email
    assert user_get.password == created_user.password
    assert user_get.roles == created_user.roles


@pytest.mark.asyncio
async def test_get_user_by_forgotten_id(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    user_dal: "UserDAL" = UserDAL(db_session)
    random_uuid: uuid.UUID = uuid.UUID("11111111-aaaa-2222-bbbb-bbbbbbbbbbbb")
    user_get: Optional[User] = await user_dal.get_user_by_id(random_uuid)
    assert not user_get


@pytest.mark.asyncio
async def test_deactivate_user(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    user_dal: "UserDAL" = UserDAL(db_session)
    created_user: Optional[User] = await _create_user(get_user, db_session)
    assert created_user
    deactivated_user_id: Optional[uuid.UUID] = await user_dal.deactivate_user(
        created_user.user_id
    )
    assert deactivated_user_id
    user: Optional[User] = await user_dal.get_user_by_id(deactivated_user_id)
    assert not user  # User is not active - should not be got


@pytest.mark.asyncio
async def test_update_user(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    user_dal: "UserDAL" = UserDAL(db_session)
    created_user: Optional[User] = await _create_user(get_user, db_session)
    assert created_user
    updated_user_id: Optional[uuid.UUID] = await user_dal.update_user(
        created_user.user_id,
        name="Updated name",
        surname="Updated surname",
        email="new_test_emai@tmail.com",
        password="qwerty321",
    )
    assert updated_user_id
    user: Optional[User] = await user_dal.get_user_by_id(updated_user_id)
    assert user
    assert get_user.name != user.name
    assert get_user.surname != user.surname
    assert get_user.email != user.email
    assert get_user.password != user.password


@pytest.mark.asyncio
async def test_set_admin_privilege(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    user_dal: "UserDAL" = UserDAL(db_session)
    created_user: Optional[User] = await _create_user(get_user, db_session)
    assert created_user
    assert created_user.roles == ["user"]
    updated_user_id: Optional[uuid.UUID] = await user_dal.set_admin_privilege(
        created_user.user_id
    )
    assert updated_user_id
    updated_user = await _get_user_by_id(created_user, db_session)
    assert updated_user
    assert updated_user.roles == ["admin"]


@pytest.mark.asyncio
async def test_revoke_admin_privilege(
    get_user: CreateUser, db_session: AsyncSession
) -> None:
    user_dal: "UserDAL" = UserDAL(db_session)
    created_user: Optional[User] = await _create_user(get_user, db_session)
    assert created_user
    assert created_user.roles == ["user"]
    updated_user_id: Optional[uuid.UUID] = await user_dal.set_admin_privilege(
        created_user.user_id
    )
    assert updated_user_id
    updated_user = await _get_user_by_id(created_user, db_session)
    assert updated_user
    assert updated_user.roles == ["admin"]
    revoked_user_id: Optional[
        uuid.UUID
    ] = await user_dal.revoke_admin_privilege(created_user.user_id)
    assert revoked_user_id
    assert created_user.roles == ["user"]
