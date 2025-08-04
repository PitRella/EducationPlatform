import logging
from abc import abstractmethod
from starlette.requests import Request

logger = logging.getLogger(__name__)


class BasePermission:
    def __init__(
            self,
            request: Request,
    ):
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


# Enforces a contract for permission validation logic.

