from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database import engine


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    async_session_maker = async_sessionmaker(
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
