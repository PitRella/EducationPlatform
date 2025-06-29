from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.DATABASE_URL, future=True, echo=True)

async_db_session = sessionmaker(  # type: ignore
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = async_db_session()
    try:
        yield session
    finally:
        await session.close()
