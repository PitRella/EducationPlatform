import uuid
from typing import Annotated

from fastapi import Depends

from src.base.dependencies import get_service
from src.users.models import User
from src.users.services import UserService


async def get_user_from_uuid(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(get_service(UserService))],
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
