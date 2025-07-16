import uuid
from abc import ABC, abstractmethod
from src.users.models import User
from typing import Protocol


class ModelWithId(Protocol):
    """Protocol for models with an ID field."""
    id: uuid.UUID | int

class ActionEnum(Protocol):
    """Protocol for enum's actions."""
    CREATE: str
    GET: str
    DELETE: str
    UPDATE: str

class BasePermissionService(ABC):

    @classmethod
    @abstractmethod
    def validate_permission(
            cls,
            target_model: ModelWithId,
            current_user: User,
            action: ActionEnum
    ) -> None:
        """Validate permissions for a given action. Or raise an error"""
        raise NotImplementedError()
