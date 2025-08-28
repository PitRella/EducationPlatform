from collections.abc import Sequence
from typing import Annotated, Literal

from fastapi import Depends, Security
from fastapi.requests import Request

from src.auth.dependencies import oauth_scheme
from src.auth.services import AuthService
from src.base.dependencies import BasePermissionDependency, get_service
from src.users.exceptions import UserIsNotAuthorException
from src.users.models import Author
from src.users.permissions import BaseAuthorPermission
from src.users.services import AuthorService


async def _get_optional_author_from_jwt(
    token: Annotated[str, Security(oauth_scheme)],
    auth_service: Annotated[AuthService, Depends(get_service(AuthService))],
    author_service: Annotated[
        AuthorService, Depends(get_service(AuthorService))
    ],
) -> Author | None:
    """Retrieve an Author from JWT token if present.

    Args:
        token (str): JWT token from the request.
        auth_service (AuthService): Service for token validation.
        author_service (AuthorService): Service for author operations.

    Returns:
        Author | None: Returns Author if token is valid, else None.

    """
    if not token:
        return None
    potential_author_id = await auth_service.validate_token_for_user(token)
    return await author_service.get_author_by_user_id(potential_author_id)


class AuthorPermissionDependency(BasePermissionDependency):
    """FastAPI dependency to validate author-related permissions.

    Applies a list of BaseAuthorPermission classes to an Author
    retrieved optionally from JWT. If no author is found or
    permissions fail, raises UserIsNotAuthorException.
    """

    def __init__(
        self,
        permissions: Sequence[type[BaseAuthorPermission]],
        logic: Literal['AND', 'OR'] = BasePermissionDependency._LOGIC_AND,
    ):
        """Initialize AuthorPermissionDependency.

        Args:
            permissions (Sequence[type[BaseAuthorPermission]]): List of
                permission classes to enforce.
            logic (Literal['AND', 'OR'], optional): Logic for combining
                permissions. Defaults to 'AND'.

        """
        super().__init__(permissions, logic)

    async def __call__(
        self,
        request: Request,
        author: Annotated[
            Author | None, Depends(_get_optional_author_from_jwt)
        ],
    ) -> Author:
        """Validate author permissions and return the Author.

        Args:
            request (Request): Current HTTP request.
            author (Author | None): Optional author from JWT token.

        Returns:
            Author: Validated author object.

        Raises:
            UserIsNotAuthorException: If author is missing or invalid.

        """
        await self._validate_permissions(
            request=request,
            author=author,
        )
        if not author:
            raise UserIsNotAuthorException
        return author
