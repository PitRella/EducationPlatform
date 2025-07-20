from typing import Annotated

from fastapi import Depends
from fastapi.params import Security
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

from src.auth.services import AuthService
from src.base.dependencies import get_service
from src.base.permission import BasePermissionService
from src.users.models import User

oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
)


async def get_user_from_jwt(
        token: Annotated[str, Security(oauth_scheme)],
        service: Annotated[AuthService, Depends(get_service(AuthService))],
) -> User:
    """Return FastAPI dependencies for authentication and validation.

    Includes:
    - OAuth2 password bearer scheme for JWT authentication.
    - Dependency to retrieve an AuthService instance.
    - Async dependency to extract a User from a JWT token.
    - Factory for a permission validation dependency
    """
    return await service.validate_token(token)


class PermissionDependency:
    def __init__(
            self,
            permission_classes: list[type[BasePermissionService]]
    ):
        self.permission_classes = permission_classes

    def __call__(self, request: Request) -> None:
        for permission_class in self.permission_classes:
            permission_class()
