from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=True
)

async_db_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> Generator:
    try:
        session: AsyncSession = async_db_session()
        yield session
    finally:
        await session.close()
