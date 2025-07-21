from typing import Annotated

from pydantic import Field, HttpUrl

from src.base.schemas import BaseSchema


class CreateAuthorRequestSchema(BaseSchema):
    """Schema for creating a creation author.

    Include Facebook and LinkedIn URLs and validated education information.
    """

    facebook_url: HttpUrl
    linkedin_url: HttpUrl
    education: Annotated[
        str, Field(min_length=10, max_length=50, pattern=r'^[a-zA-Z ]+$')
    ]
