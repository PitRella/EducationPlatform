from abc import abstractmethod, ABC
from fastapi import Request


class BasePermissionService(ABC):
    @abstractmethod
    def validate_permission(self, request: Request) -> None: ...
