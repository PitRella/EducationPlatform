import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User
from src.users.service import UserService

__all__ = ['get_service', 'get_user_from_uuid']


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    """Return a UserService instance with a database session dependency.

    Args:
        db (AsyncSession, optional): Database session provided
        by dependency injection.

    Returns:
        UserService: An instance of UserService initialized
         with the given session.

    """
    return UserService(db_session=db)


async def get_user_from_uuid(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(get_service)],
) -> User:
    """Retrieve a User instance by UUID using the UserService dependency.

    Args:
        user_id (uuid.UUID): The unique identifier of the user.
        service (UserService, optional): Dependency-injected
        UserService instance.

    Returns:
        User: The user object corresponding to the given UUID.

    Raises:
        UserNotFoundByIdException: If no user is found with the provided UUID.

    """
    return await service.get_user_by_id(user_id=user_id)
