import logging
from abc import ABC, abstractmethod
from starlette.requests import Request
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
    async def validate_permission(
            self,
    ) -> None:
        """Abstract method that must be implemented by all permission classes.
        Should raise an exception if the permission check fails.
        """
        ...

