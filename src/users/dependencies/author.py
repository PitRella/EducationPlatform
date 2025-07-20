from typing import Annotated
from fastapi import Depends

from src.auth.dependencies import get_user_from_jwt
from src.base.dependencies import get_service
from src.users.models import User, Author
from src.users.services import AuthorService


async def get_author_from_jwt(
        user: Annotated[User, Depends(get_user_from_jwt)],
        service: Annotated[AuthorService, Depends(get_service(AuthorService))]
) -> Author:
    return await service.is_user_author(user)
