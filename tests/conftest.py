import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.users.schemas import CreateUser, UpdateUserRequest
from src.settings import DATABASE_URL


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
async def db():  # type: ignore
    engine = create_async_engine(DATABASE_URL, future=True)
    async_session = sessionmaker(  # type: ignore
        engine, expire_on_commit=False, class_=AsyncSession
    )
    yield async_session
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db):  # type: ignore
    async with db() as session:
        async with session.begin():
            yield session
            await session.rollback()
        await session.close()
