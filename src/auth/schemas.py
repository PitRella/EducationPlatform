from pydantic import BaseModel


class Token(BaseModel):
    """Pydantic model for token."""

    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'  # noqa: S105
