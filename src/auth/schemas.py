import uuid

from pydantic import BaseModel

from src.base.schemas import BaseSchema


class Token(BaseModel):
    """Pydantic model for token."""

    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'  # noqa: S105


class CreateRefreshTokenSchema(BaseSchema):
    """Pydantic model for creating a new refresh token session.

    This schema defines the structure for creating a new refresh token session
    in the database. It includes the user ID, refresh token value.

    Attributes:
        user_id (uuid.UUID): The ID of the user for whom the token is created.
        refresh_token (uuid.UUID): The unique refresh token value.
        expires_in (float): The total seconds until.

    """

    user_id: uuid.UUID
    refresh_token: uuid.UUID
    expires_in: float
