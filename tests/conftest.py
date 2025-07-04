import uuid

import pytest
import pytest_asyncio
from _pytest.fixtures import FixtureRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.database import engine
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
        user_roles=['user'],  # type: ignore
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
