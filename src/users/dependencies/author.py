from typing import Annotated

from fastapi import Depends, Security

from src.auth.dependencies import oauth_scheme
from src.auth.services import AuthService
from src.base.dependencies import get_service
from src.users.exceptions import UserIsNotAuthorException
from src.users.models import Author
from src.users.permissions import BaseAuthorPermission
from src.users.services import AuthorService
from fastapi.requests import Request

async def get_optional_author_from_jwt(
    token: Annotated[str, Security(oauth_scheme)],
    auth_service: Annotated[AuthService, Depends(get_service(AuthService))],
    author_service: Annotated[
        AuthorService, Depends(get_service(AuthorService))
    ],
) -> Author | None:
    if not token:
        return None
    potential_author_id = await auth_service.validate_token_for_user(token)
    return await author_service.get_author_by_user_id(potential_author_id)


class AuthorPermissionDependency:
    def __init__(self, permissions: list[type[BaseAuthorPermission]]):
        self.permissions = permissions

    async def __call__(
            self,
            request: Request,
            author: Annotated[Author | None, Depends(get_optional_author_from_jwt)],
    ) -> Author:
        """Callable used as a FastAPI dependency.

        It receives the request and
        authenticated user, applies all permission classes, and raises
        if any permission fails.
        """
        for permission_cls in self.permissions:
            # Instantiate permission with request and user
            p_class = permission_cls(request=request, author=author)
            #  the actual permission check
            await p_class.validate_permission()
        # Just to be sure that the user is authenticated after the permission check.
        if not author:
            raise UserIsNotAuthorException
        return author
