from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.auth.dependencies import UserPermissionDependency
from src.auth.permissions import IsAuthenticated
from src.base.dependencies import get_service
from src.users.models import User
from src.users.schemas import (
    CreateUserRequestSchema,
    UpdateUserRequestSchema,
    UpdateUserResponseSchema,
    UserResponseShema,
)
from src.users.services import UserService

user_router = APIRouter()


@user_router.get(
    '/me',
    description='Get information about current user',
    response_model=UserResponseShema,
)
async def get_me(
    user: Annotated[
        User, Security(UserPermissionDependency([IsAuthenticated]))
    ],
) -> UserResponseShema:
    """Retrieve the currently authenticated user's information.

    Args:
        user (User): The authenticated user retrieved via security dependency.

    Returns:
        UserResponseShema: Schema representing the current user's data.

    """
    return UserResponseShema.model_validate(user)


@user_router.post(
    '/', description='Create a new user', response_model=UserResponseShema
)
async def create_user(
    user_schema: CreateUserRequestSchema,
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> UserResponseShema:
    """Create a new user in the system.

    Args:
        user_schema (CreateUserRequestSchema): Schema with new user data.
        service (UserService): Service for user-related operations.

    Returns:
        UserResponseShema: Schema representing the newly created user.

    """
    new_user = await service.create_new_user(user=user_schema)
    return UserResponseShema.model_validate(new_user)


@user_router.patch(
    '/me',
    description='Update information about current user',
    response_model=UpdateUserResponseSchema,
)
async def update_user(
    user: Annotated[
        User, Security(UserPermissionDependency([IsAuthenticated]))
    ],
    user_fields: UpdateUserRequestSchema,
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> UpdateUserResponseSchema:
    """Update the currently authenticated user's information.

    Args:
        user (User): The authenticated user retrieved via security dependency.
        user_fields (UpdateUserRequestSchema): Schema with fields to update.
        service (UserService): Service for user-related operations.

    Returns:
        UpdateUserResponseSchema: Schema representing the updated user.

    """
    updated_user = await service.update_user(
        target_user=user, user_fields=user_fields
    )
    return UpdateUserResponseSchema.model_validate(updated_user)


@user_router.delete('/me', status_code=204)
async def deactivate_user(
    user: Annotated[
        User, Security(UserPermissionDependency([IsAuthenticated]))
    ],
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> None:
    """Deactivate the currently authenticated user's account.

    Args:
        user (User): The authenticated user retrieved via security dependency.
        service (UserService): Service for user-related operations.

    Returns:
        None

    """
    await service.deactivate_user(target_user=user)
