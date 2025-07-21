from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.dependencies import get_user_from_jwt
from src.base.dependencies import get_service
from src.users.models import Author, User
from src.users.schemas import CreateAuthorRequestSchema
from src.users.services import AuthorService

author_router = APIRouter()


@author_router.post('/become_author', response_model=CreateAuthorRequestSchema)
async def become_author(
    author_schema: CreateAuthorRequestSchema,
    user: Annotated[User, Depends(get_user_from_jwt)],
    service: Annotated[AuthorService, Depends(get_service(AuthorService))],
) -> CreateAuthorRequestSchema:
    """Endpoint for users to request author status.

    Creates a new author profile for the authenticated user if eligible
    and returns the created author data.
    """
    new_author: Author = await service.become_author(
        user=user, author_schema=author_schema
    )
    return CreateAuthorRequestSchema.model_validate(new_author)
