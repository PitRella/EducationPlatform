import logging
from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from src.auth.dependencies import get_user_from_jwt
from src.users.models import User

logger = logging.getLogger(__name__)


# Abstract base class for all permission services.
# Enforces a contract for permission validation logic.
class BasePermissionService(ABC):
    def __init__(
        self,
        user: User,
        request: Request,
    ):
        # The current authenticated user
        self.user: User = user

        # The current HTTP request
        self.request: Request = request

    @abstractmethod
    def validate_permission(
        self,
    ) -> None:
        """Abstract method that must be implemented by all permission classes.
        Should raise an exception if the permission check fails.
        """
        ...


# Concrete permission that checks if a user is authenticated.
# Can be extended to perform additional checks if needed.
class IsAuthenticated(BasePermissionService):
    def validate_permission(
        self,
    ) -> None:
        """Implement actual logic to verify if the user is authenticated.
        Raise exception if not.
        """


# Dependency that applies a list of permission classes to a route.
# Each permission is initialized, and its validate_permission() is called.
class PermissionDependency:
    def __init__(self, permissions: list[type[BasePermissionService]]):
        # Store a list of permission class types to be validated later
        self.permissions = permissions

    def __call__(
        self,
        request: Request,
        user: Annotated[User, Depends(get_user_from_jwt)],
    ) -> User:
        """Callable used as a FastAPI dependency. It receives the request and
        authenticated user, applies all permission classes, and raises
        if any permission fails.
        """
        for permission_cls in self.permissions:
            # Instantiate permission with request and user
            p_class = permission_cls(request=request, user=user)

            # Perform the actual permission check
            p_class.validate_permission()

        # If all checks pass, return the user
        return user
