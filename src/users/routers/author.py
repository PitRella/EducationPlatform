from typing import Annotated

from fastapi import APIRouter, Depends

from src.base.dependencies import get_service
from src.auth.dependencies import get_user_from_jwt
from src.users.models import User
from src.users.schemas import CreateAuthorRequestSchema
from src.users.services import AuthorService

author_router = APIRouter()


@author_router.post('/become_author', response_model=CreateAuthorRequestSchema)
async def become_author(
        author_schema: CreateAuthorRequestSchema,
        user: Annotated[User, Depends(get_user_from_jwt)],
        service: Annotated[AuthorService, Depends(get_service(AuthorService))],
):
    return await service.become_author(user=user, author_schema=author_schema)
