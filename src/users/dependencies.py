from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.service import UserService

from src.database import get_db

__all__ = ["get_service"]


def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency for retrieving the UserService instance."""
    return UserService(db_session=db)
