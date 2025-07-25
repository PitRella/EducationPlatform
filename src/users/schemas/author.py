import uuid
from typing import Annotated, Optional
from decimal import Decimal
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

class AuthorResponseSchema(BaseSchema):
    """Schema for author response."""
    id: uuid.UUID
    user_id: uuid.UUID
    slug: str
    is_verified: bool
    balance: Decimal
    facebook_url: str
    linkedin_url: str
    education: str
    country: Optional[str]
    city: Optional[str]
    phone: Optional[str]
    website: Optional[str]