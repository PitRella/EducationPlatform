import re
from typing import Optional, Sequence
from src.users.enums import UserRoles

from fastapi.exceptions import HTTPException

from pydantic import BaseModel, field_validator, ConfigDict, Field

import uuid

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        model_config = ConfigDict(from_attributes=True)


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: str
    is_active: bool
    user_roles: Sequence[str]


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=10)
    surname: Optional[str] = Field(default=None, min_length=3, max_length=10)
    email: Optional[str] = Field(default=None, min_length=3, max_length=50)

    @classmethod
    @field_validator("name")
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail="Name should contain only letters (a-z, A-Z, а-я, А-Я, -).",
            )
        return value

    @classmethod
    @field_validator("surname")
    def validate_surname(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail="Surname should contain only letters (a-z, A-Z, а-я, А-Я, -).",
            )
        return value


class UpdateUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class CreateUser(BaseModel):
    name: str
    surname: str
    email: str
    password: str
    user_roles: Optional[Sequence[UserRoles]] = None

    @classmethod
    @field_validator("name")
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail="Name should contain only letters (a-z, A-Z, а-я, А-Я, -).",
            )
        return value

    @classmethod
    @field_validator("surname")
    def validate_surname(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422,
                detail="Surname should contain only letters (a-z, A-Z, а-я, А-Я, -).",
            )
        return value
