import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Security

from src.auth.dependencies import PermissionDependency
from src.auth.permissions import IsAuthenticated
from src.base.dependencies import get_service
from src.users.dependencies import AuthorPermissionDependency
from src.users.models import Author, User
from src.users.permissions import IsAuthorPermission
from src.users.schemas import AuthorResponseSchema, CreateAuthorRequestSchema
from src.users.services import AuthorService

author_router = APIRouter()


@author_router.post(
    '/become_author',
    description='Became an author',
    response_model=AuthorResponseSchema,
)
async def become_author(
        author_schema: CreateAuthorRequestSchema,
        user: Annotated[
            User, Security(PermissionDependency([IsAuthenticated]))],
        service: Annotated[AuthorService, Depends(get_service(AuthorService))],
) -> AuthorResponseSchema:
    """Endpoint to create a new author profile for a user.

    Args:
        author_schema (CreateAuthorRequestSchema): The author creation data.
        user (User): The authenticated user attempting to become an author.
        service (AuthorService): The author service instance.

    Returns:
        AuthorResponseSchema: The newly created author data.

    """
    new_author: Author = await service.become_author(
        user=user, author_schema=author_schema
    )
    return AuthorResponseSchema.model_validate(new_author)


@author_router.get(
    '/me',
    description='Get information about current author',
    response_model=AuthorResponseSchema,
)
async def get_current_author(
        author: Annotated[
            Author, Security(
                AuthorPermissionDependency([IsAuthorPermission]))],
) -> AuthorResponseSchema:
    """Endpoint to retrieve the current authenticated author's information.

    Returns:
        AuthorResponseSchema: The author data for the user.

    """
    return AuthorResponseSchema.model_validate(author)


@author_router.get(
    '/{author_id}',
    description='Get information about an author by ID',
    response_model=AuthorResponseSchema,
)
async def get_author_by_id(
        author_id: uuid.UUID,
        service: Annotated[AuthorService, Depends(get_service(AuthorService))],
) -> AuthorResponseSchema:
    """Endpoint to retrieve author information by their ID.

    Args:
        author_id (uuid.UUID): The unique identifier of the author to retrieve.
        service (AuthorService): The author service instance.

    Returns:
        AuthorResponseSchema: The author data for the specified ID.

    """
    author = await service.get_author_by_id(author_id)
    return AuthorResponseSchema.model_validate(author)
