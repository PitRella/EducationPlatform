import uuid
from typing import Annotated

from fastapi import APIRouter, Security

from src.users import User
from src.users.dependencies import UserPermissionDependency
from src.users.permissions import BaseUserPermission
from src.users.schemas import UserResponseShema

admin_router = APIRouter()


@admin_router.get('/{user_id}')
def get_user_by_id(
    user: Annotated[
        User, Security(UserPermissionDependency([BaseUserPermission]))
    ],
) -> UserResponseShema:
    """Get user information by their UUID if permissions allow.

    Args:
        user_id (uuid.UUID): Unique identifier of the user to retrieve
        user (User): Currently authenticated user making the request.
            Must have appropriate permissions via BaseUserPermission.

    Returns:
        UserResponseShema: Validated user data response model

    Raises:
        UserPermissionException: If an authenticated user lacks permissions,
        UserNotFoundByIdException: If no user exists with the provided UUID

    """
    return UserResponseShema.model_validate(user)
