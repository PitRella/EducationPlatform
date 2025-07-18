from typing import Annotated

from fastapi import APIRouter, Depends

from src.base.dependencies import get_service
from src.users.dependencies import get_user_from_uuid
from src.users.models import User
from src.users.schemas import CreateAuthorRequestSchema
from src.users.services import AuthorService

author_router = APIRouter()


@author_router.post('/', response_model=CreateAuthorRequestSchema)
async def create_author(
    user: Annotated[User, Depends(get_user_from_uuid)],
    service: Annotated[AuthorService, Depends(get_service(AuthorService))],
):
    await service.create_new_author(user=user)
