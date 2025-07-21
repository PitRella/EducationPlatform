from typing import Annotated

from pydantic import HttpUrl, Field
from src.base.schemas import BaseSchema


class CreateAuthorRequestSchema(BaseSchema):
    facebook_url: HttpUrl
    linkedin_url: HttpUrl
    education: Annotated[
        str, Field(min_length=10, max_length=50, pattern=r'^[a-zA-Z ]+$')
    ]