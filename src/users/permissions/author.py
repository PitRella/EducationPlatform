from abc import ABC
from typing import Unpack

from fastapi.requests import Request

from src.base.permission import BasePermission, PermissionKwargs
from src.users import Author
from src.users.exceptions import (
    UserPermissionException,
)


class BaseAuthorPermission(BasePermission, ABC):
    """Abstract base class for author-related permissions.

    Provides access to the author object from dependency kwargs and a method
    to check if the author is authorized.
    """

    def __init__(
        self,
        request: Request,
        **kwargs: Unpack[PermissionKwargs],
    ):
        """Initialize the base author permission.

        Args:
            request (Request): The current HTTP request.
            **kwargs (PermissionKwargs): Additional keyword arguments,
                including the 'author'.

        """
        super().__init__(request, **kwargs)
        self.author: Author | None = kwargs.get('author')

    def _is_author_authorized(self) -> Author:
        """Check if an author is authorized.

        Raises:
            UserPermissionException: If the author is not provided.

        Returns:
            Author: The authenticated author.

        """
        if not self.author:
            raise UserPermissionException
        return self.author


class IsAuthorPermission(BaseAuthorPermission):
    """Permission class to validate that the current user is an author."""

    async def validate_permission(self) -> None:
        """Validate that the current user is an authorized author.

        Raises:
            UserPermissionException: If the author is not authorized.

        """
        self._is_author_authorized()
