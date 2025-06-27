import pytest

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.users.schemas import CreateUser
from src.settings import DATABASE_URL


@pytest.fixture
def get_user() -> CreateUser:
    return CreateUser(
        name="TestName",
        surname="TestSurName",
        email="test_user@tmail.com",
        password="qwerty123",
        user_roles=["user"],  # type: ignore
    )


@pytest_asyncio.fixture
async def db_session():  # type: ignore
    engine = create_async_engine(DATABASE_URL, future=True)
    async_session = sessionmaker(  # type: ignore
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()
        await session.close()
    await engine.dispose()
