import re
import uuid
from collections.abc import Sequence
from typing import Annotated

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)

from src.base.schemas import BaseSchema
from src.users.enums import UserRoles
from src.users.exceptions import (
    BadEmailSchemaException,
    BadPasswordSchemaException,
)

PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$'
)

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


class UserResponseShema(BaseSchema):
    """Pydantic model for showing user information."""

    id: uuid.UUID
    name: str
    surname: str
    email: str
    is_active: bool


class CreateUserRequestSchema(BaseModel):
    """Pydantic model for creating a new user."""

    name: Annotated[
        str, Field(min_length=3, max_length=15, pattern='^[a-zA-Z]+$')
    ]
    surname: Annotated[
        str, Field(min_length=3, max_length=15, pattern='^[a-zA-Z]+$')
    ]
    email: EmailStr
    password: Annotated[
        SecretStr,
        Field(
            min_length=8,
            max_length=50,
        ),
    ]
    role: Sequence[UserRoles] | None = None

    @field_validator('email')
    def validate_email(cls, value: str) -> str:
        """Validate the email address using regex."""
        if not EMAIL_PATTERN.match(value):
            raise BadEmailSchemaException
        return value

    @field_validator('password', mode='before')
    def validate_password(cls, value: str) -> str:
        """Validate the password using regex."""
        if not PASSWORD_PATTERN.match(value):
            raise BadPasswordSchemaException
        return value


class DeleteUserResponseSchema(BaseSchema):
    """Pydantic model for deleting user response."""

    id: uuid.UUID


class UpdateUserRequestSchema(BaseModel):
    """Pydantic model for updating user information."""

    name: str | None = Field(default=None, min_length=3, max_length=10)
    surname: str | None = Field(default=None, min_length=3, max_length=10)
    email: EmailStr | None = Field(default=None, min_length=3, max_length=50)


class UpdateUserResponseSchema(BaseSchema):
    """Pydantic model for updating user response."""

    id: uuid.UUID
