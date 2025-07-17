from abc import ABC, abstractmethod

from src.database import Base
from src.users.models import User
from typing import Protocol, TypeVar

Model = TypeVar('Model', bound=Base)


class EnumWithCRUD(Protocol):
    """Protocol for enum's actions."""
    CREATE: str
    GET: str
    DELETE: str
    UPDATE: str


class BasePermissionService[Model](ABC):

    @classmethod
    @abstractmethod
    def validate_permission(
            cls,
            target_model: Model,
            current_user: User,
            action: EnumWithCRUD
    ) -> None:
        """
        Validate if the current user has permission
        to perform an action on a target model.

        Args:
            target_model: The database model instance to check permissions against
            current_user: The user attempting to perform the action
            action: The action being attempted (CREATE, GET, DELETE, UPDATE)

        Returns:
            None if validation succeeds

        Raises:
            NotImplementedError: When a child does not implement a method
            PermissionError: When the user doesn't have required permissions
        """

        raise NotImplementedError()
