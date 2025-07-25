import uuid
from typing import Annotated

from fastapi import APIRouter, Security

from src.users import User
from src.users.dependencies import UserPermissionDependency
from src.users.permissions import BaseUserPermission
from src.users.schemas import UserResponseShema

admin_router = APIRouter()


@admin_router.get("/{user_id}")
def get_user_by_id(
        user_id: uuid.UUID,
        user: Annotated[
            User, Security(UserPermissionDependency([BaseUserPermission]))
        ],
) -> UserResponseShema:
    return UserResponseShema.model_validate(user)
