import re
import uuid
from collections.abc import Sequence
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)

from src.users.enums import UserRoles
from src.users.exceptions import (
    BadEmailSchemaException,
    BadPasswordSchemaException,
)

PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$'
)

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


class BaseTunedModelSchema(BaseModel):
    """Base model for all models in the application.

    Provided configuration to create models from an orm object.
    """

    model_config = ConfigDict(from_attributes=True)


class CreateUserResponseShema(BaseTunedModelSchema):
    """Pydantic model for showing user information."""

    user_id: uuid.UUID
    name: str
    surname: str
    email: str
    is_active: bool
    roles: Sequence[str]


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
    roles: Sequence[UserRoles] | None = None

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


class DeleteUserResponseSchema(BaseModel):
    """Pydantic model for deleting user response."""

    deleted_user_id: uuid.UUID


class UpdateUserRequestSchema(BaseModel):
    """Pydantic model for updating user information."""

    name: str | None = Field(default=None, min_length=3, max_length=10)
    surname: str | None = Field(default=None, min_length=3, max_length=10)
    email: EmailStr | None = Field(default=None, min_length=3, max_length=50)


class UpdateUserResponseSchema(BaseModel):
    """Pydantic model for updating user response."""

    updated_user_id: uuid.UUID
