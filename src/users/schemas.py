import re
import uuid
from collections.abc import Sequence

from fastapi.exceptions import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.users.enums import UserRoles

LETTER_MATCH_PATTERN = re.compile(r'^[а-яА-Яa-zA-Z\-]+$')


class TunedModel(BaseModel):
    """Base model for all models in the application."""

    model_config = ConfigDict(from_attributes=True)


class ShowUser(TunedModel):
    """Pydantic model for showing user information."""

    user_id: uuid.UUID
    name: str
    surname: str
    email: str
    is_active: bool
    roles: Sequence[str]


class DeleteUserResponse(BaseModel):
    """Pydantic model for deleting user response."""

    deleted_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    """Pydantic model for updating user information."""

    name: str | None = Field(default=None, min_length=3, max_length=10)
    surname: str | None = Field(default=None, min_length=3, max_length=10)
    email: str | None = Field(default=None, min_length=3, max_length=50)

    @classmethod
    @field_validator('name')
    def validate_name(cls, value: str | None) -> str | None:
        """Validate name name field."""
        if value is not None and not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail='Name should contain only letters'
                ' (a-z, A-Z, a-я, A-Я, -).',
            )
        return value

    @classmethod
    @field_validator('surname')
    def validate_surname(cls, value: str | None) -> str | None:
        """Validate surname name field."""
        if value is not None and not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail='Surname should contain only letters'
                ' (a-z, A-Z, a-я, A-Я, -).',
            )
        return value


class UpdateUserResponse(BaseModel):
    """Pydantic model for updating user response."""

    updated_user_id: uuid.UUID


class CreateUser(BaseModel):
    """Pydantic model for creating a new user."""

    name: str
    surname: str
    email: str
    password: str
    roles: Sequence[UserRoles] | None = None

    @classmethod
    @field_validator('name')
    def validate_name(cls, value: str | None) -> str | None:
        """Validate surname name field."""
        if value is not None and not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail='Name should contain only letters'
                ' (a-z, A-Z, a-я, A-Я, -).',
            )
        return value

    @classmethod
    @field_validator('surname')
    def validate_surname(cls, value: str | None) -> str | None:
        """Validate surname field."""
        if value is not None and not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail='Surname should contain only letters'
                ' (a-z, A-Z, a-я, A-Я, -).',
            )
        return value
