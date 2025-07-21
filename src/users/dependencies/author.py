from typing import Annotated
from fastapi import Depends, Security

from src.auth.dependencies import get_user_from_jwt, oauth_scheme
from src.auth.services import AuthService
from src.base.dependencies import get_service
from src.users.models import User, Author
from src.users.services import AuthorService


async def get_author_from_jwt(
        token: Annotated[str, Security(oauth_scheme)],
        auth_service: Annotated[AuthService, Depends(get_service(AuthService))],
        author_service: Annotated[AuthorService, Depends(get_service(AuthorService))]
) -> Author:
    potential_author_id = await auth_service.validate_token_for_user(token)
    return await author_service.is_user_author(potential_author_id)
