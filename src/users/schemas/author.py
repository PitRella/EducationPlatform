import uuid

from pydantic import HttpUrl

from src.base.schemas import BaseSchema


class CreateAuthorRequestSchema(BaseSchema):
    user_id: uuid.UUID
    facebook_url: HttpUrl
    linkedin_url: HttpUrl
    education: HttpUrl
