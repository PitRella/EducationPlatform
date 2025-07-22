from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TypeVar, Optional, Annotated

from fastapi import Depends, HTTPException
from starlette.requests import Request

from src.auth.services import AuthService
from src.base.dependencies import get_service
from src.database import Base
from src.users.models import User
from src.users.services import UserService


class BasePermissionService(ABC):
    def __init__(self, user: User):
        self.user = user

    @classmethod
    async def create(
            cls,
            request: Request,
            auth_service: Annotated[
                AuthService, Depends(get_service(AuthService))],
            user_service: Annotated[
                UserService, Depends(get_service(UserService))],
    ) -> BasePermissionService:
        token: str | None = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=404,
                                detail="No access token found")
        user_id = await auth_service.validate_token_for_user(token)
        user = await user_service.get_user_by_id(user_id)
        return cls(user)

    @abstractmethod
    def validate_permission(
            self,
            request: Request
    ) -> None:
        ...


class PermissionDependency:
    def __init__(self, permissions: list[BasePermissionService]):
        self.permissions = permissions

    def __call__(self, request: Request) -> None:
        for permission in self.permissions:
            permission.validate_permission(request)
