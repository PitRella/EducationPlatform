from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TypeVar

from src.database import Base
from src.users.models import User

Model = TypeVar('Model', bound=Base)
ActionEnum = TypeVar('ActionEnum', bound=StrEnum)


class BasePermissionService[Model, ActionEnum](ABC):
    @classmethod
    @abstractmethod
    def validate_permission(
        cls, target_model: Model, current_user: User, action: ActionEnum
    ) -> None:
        """Validate if the current user has permission
        to perform an a ction on a target model.

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
        raise NotImplementedError
