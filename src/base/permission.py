import logging
from abc import ABC, abstractmethod

from starlette.requests import Request

from src.users.models import User

logger = logging.getLogger(__name__)


# Abstract base class for all permission services.
# Enforces a contract for permission validation logic.
class BasePermissionService(ABC):
    """Abstract base class for implementing permission validation.

    Provides a standardized interface for permission checking.
    All permission services must inherit from this class and implement the
    validate_permission() method to enforce their specific access control rules.

    Attributes:
        user (User): The authenticated user making the request
        request (Request): The current HTTP request being processed

    """

    def __init__(
        self,
        user: User,
        request: Request,
    ):
        """Initialize BasePermissionService with user and request.

        Base class for implementing permission validation logic.
        All permission services should inherit from this class
        and implement validate_permission().

        Args:
            user (User): The authenticated user making the request
            request (Request): The current HTTP request being processed

        The class provides core functionality for permission checking
        by storing the authenticated user and current request context.

        """
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
