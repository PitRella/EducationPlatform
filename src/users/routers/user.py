from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.auth.dependencies import PermissionDependency
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
    user: Annotated[User, Security(PermissionDependency([IsAuthenticated]))],
) -> UserResponseShema:
    """Endpoint to update get a user from token."""
    return UserResponseShema.model_validate(user)


@user_router.post(
    '/me',
    description='Create a new user',
    response_model=UserResponseShema
)
async def create_user(
    user_schema: CreateUserRequestSchema,
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> UserResponseShema:
    """Endpoint to create a new user."""
    new_user = await service.create_new_user(user=user_schema)
    return UserResponseShema.model_validate(new_user)


@user_router.patch(
    '/me',
    description='Update information about current user',
    response_model=UpdateUserResponseSchema,
)
async def update_user(
    user: Annotated[User, Security(PermissionDependency([IsAuthenticated]))],
    user_fields: UpdateUserRequestSchema,
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> UpdateUserResponseSchema:
    """Endpoint to update info about a user."""
    updated_user = await service.update_user(
        target_user=user, user_fields=user_fields
    )
    return UpdateUserResponseSchema.model_validate(updated_user)


@user_router.delete('/me', status_code=204)
async def deactivate_user(
    user: Annotated[User, Security(PermissionDependency([IsAuthenticated]))],
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> None:
    """Endpoint to deactivate the user."""
    return await service.deactivate_user(target_user=user)
