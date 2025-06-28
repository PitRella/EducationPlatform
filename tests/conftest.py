import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.session import engine
from src.users.schemas import CreateUser, UpdateUserRequest


@pytest_asyncio.fixture
async def test_user_schema() -> CreateUser:
    return CreateUser(
        name="TestName",
        surname="TestSurName",
        email="test_user@tmail.com",
        password="qwerty123",
        user_roles=["user"],  # type: ignore
    )


@pytest_asyncio.fixture
async def update_user_schema() -> UpdateUserRequest:
    return UpdateUserRequest(
        name="uname",
        surname="usurname",
        email="uemail",
    )


@pytest_asyncio.fixture
async def async_session_maker():  # type: ignore
    async_session_maker = sessionmaker(  # type: ignore
        engine, expire_on_commit=False, class_=AsyncSession
    )
    yield async_session_maker
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_session_maker):  # type: ignore
    session: AsyncSession = async_session_maker()
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture
async def db_started_session(db_session):  # type: ignore
    async with db_session.begin():
        yield db_session
        await db_session.rollback()
