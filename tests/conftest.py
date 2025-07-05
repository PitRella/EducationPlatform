import uuid

import pytest
import pytest_asyncio
from _pytest.fixtures import FixtureRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.database import engine
from src.users.enums import UserRoles
from src.users.models import User
from src.users.schemas import CreateUser, UpdateUserRequest


@pytest.fixture
def test_user(request: FixtureRequest) -> User:
    return request.getfixturevalue(request.param)  # type: ignore


@pytest_asyncio.fixture
async def user_schema() -> CreateUser:
    return CreateUser(
        name='TestName',
        surname='TestSurName',
        email='test_user@tmail.com',
        password='qwerty123',
        roles=['user'],  # type: ignore
    )


@pytest_asyncio.fixture
async def default_user_obj() -> User:
    return User(
        user_id=uuid.uuid4(),
        name='TestName',
        surname='TestSurName',
        email='test_user@tmail.com',
        password='qwerty123',
        roles=['user'],
        is_active=True,
    )


@pytest_asyncio.fixture
async def admin_user_obj() -> User:
    return User(
        user_id=uuid.uuid4(),
        name='AdminTestName',
        surname='AdminTestSurName',
        email='admin_test_user@tmail.com',
        password='qwerty123',
        roles=['admin'],
        is_active=True,
    )


@pytest_asyncio.fixture
async def superadmin_user_obj() -> User:
    return User(
        user_id=uuid.uuid4(),
        name='AdminTestName',
        surname='AdminTestSurName',
        email='admin_test_user@tmail.com',
        password='qwerty123',
        roles=['superadmin'],
        is_active=True,
    )


@pytest_asyncio.fixture
async def update_user_schema() -> UpdateUserRequest:
    return UpdateUserRequest(
        name='uname',
        surname='usurname',
        email='uemail',
    )


@pytest_asyncio.fixture
async def db_session():  # type: ignore
    async_session_maker = sessionmaker(  # type: ignore
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    session: AsyncSession = async_session_maker()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def db_started_session(db_session):  # type: ignore
    async with db_session.begin():
        yield db_session
        await db_session.rollback()


class MockUserDAO:
    def __init__(self, user_obj: User):
        """Initialize MockUserDAO."""
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
