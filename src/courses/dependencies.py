from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.courses.service import CourseService
from src.database import get_db


async def get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CourseService:
    """Return a CourseService instance with a database session dependency."""
    return CourseService(db_session=db)
