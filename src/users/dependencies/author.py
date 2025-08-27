from typing import Annotated, Sequence, Literal

from fastapi import Depends, Security

from src.auth.dependencies import oauth_scheme
from src.auth.services import AuthService
from src.base.dependencies import get_service, BasePermissionDependency
from src.users.exceptions import UserIsNotAuthorException
from src.users.models import Author
from src.users.permissions import BaseAuthorPermission
from src.users.services import AuthorService
from fastapi.requests import Request


async def _get_optional_author_from_jwt(
        token: Annotated[str, Security(oauth_scheme)],
        auth_service: Annotated[
            AuthService, Depends(get_service(AuthService))],
        author_service: Annotated[
            AuthorService, Depends(get_service(AuthorService))
        ],
) -> Author | None:
    if not token:
        return None
    potential_author_id = await auth_service.validate_token_for_user(token)
    return await author_service.get_author_by_user_id(potential_author_id)


class AuthorPermissionDependency(BasePermissionDependency):
    def __init__(
            self,
            permissions: Sequence[type[BaseAuthorPermission]],
            logic: Literal["AND", "OR"] = BasePermissionDependency._LOGIC_AND):
        super().__init__(permissions, logic)

    async def __call__(
            self,
            request: Request,
            author: Annotated[
                Author | None, Depends(_get_optional_author_from_jwt)],
    ) -> Author:
        await self._validate_permissions(
            request=request,
            author=author,
        )
        if not author:
            raise UserIsNotAuthorException
        return author
