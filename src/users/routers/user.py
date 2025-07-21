from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.auth.dependencies import validate_user_permission
from src.auth.enums import UserAction
from src.base.dependencies import get_service
from src.users.models import User
from src.users.schemas import (
    CreateUserRequestSchema,
    CreateUserResponseShema,
    UpdateUserRequestSchema,
    UpdateUserResponseSchema,
)
from src.users.services import UserService

user_router = APIRouter()


@user_router.post('/', response_model=CreateUserResponseShema)
async def create_user(
    user: CreateUserRequestSchema,
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> CreateUserResponseShema:
    """Endpoint to create a new user."""
    new_user = await service.create_new_user(user=user)
    return CreateUserResponseShema.model_validate(new_user)


@user_router.delete('/{user_id}', status_code=204)
async def deactivate_user(
    user: Annotated[User, Security(validate_user_permission(UserAction.GET))],
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> None:
    """Endpoint to deactivate the user."""
    return await service.deactivate_user(target_user=user)


@user_router.get('/{user_id}', response_model=CreateUserResponseShema)
async def get_user_by_id(
    user: Annotated[User, Security(validate_user_permission(UserAction.GET))],
) -> CreateUserResponseShema:
    """Endpoint to update get a user."""
    return CreateUserResponseShema.model_validate(user)


@user_router.patch('/{user_id}', response_model=UpdateUserResponseSchema)
async def update_user(
    user: Annotated[User, Depends(validate_user_permission(UserAction.UPDATE))],
    user_fields: UpdateUserRequestSchema,
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> UpdateUserResponseSchema:
    """Endpoint to update info about a user."""
    updated_user = await service.update_user(
        target_user=user, user_fields=user_fields
    )
    return UpdateUserResponseSchema.model_validate(updated_user)


@user_router.patch('/set_admin_privilege/{user_id}')
async def set_admin_privilege(
    user: Annotated[
        User,
        Depends(validate_user_permission(UserAction.SET_ADMIN_PRIVILEGE)),
    ],
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> UpdateUserResponseSchema:
    """Endpoint to set admin privileges to a user."""
    updated_user = await service.set_admin_privilege(
        target_user=user,
    )
    return UpdateUserResponseSchema.model_validate(updated_user)


@user_router.patch('/revoke_admin_privilege/{user_id}')
async def revoke_admin_privilege(
    service: Annotated[UserService, Depends(get_service(UserService))],
    user: Annotated[
        User,
        Security(validate_user_permission(UserAction.REVOKE_ADMIN_PRIVILEGE)),
    ],
) -> UpdateUserResponseSchema:
    """Endpoint to revoke admin privileges from a user."""
    updated_user = await service.revoke_admin_privilege(target_user=user)
    return UpdateUserResponseSchema.model_validate(updated_user)
