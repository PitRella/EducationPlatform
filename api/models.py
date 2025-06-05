import re

from fastapi.exceptions import HTTPException

from pydantic import BaseModel, field_validator, ConfigDict
import uuid

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-яa-zA-Z\-]+$]")


class TunedModel(BaseModel):
    class Config:
        model_config = ConfigDict(from_attributes=True)


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: str
    is_active: bool

class CreateUser(BaseModel):
    name: str
    surname: str
    email: str

    @classmethod
    @field_validator("name")
    def validate_name(cls, value: str):
        if not value in LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contain only letters."
            )
        return value

    @classmethod
    @field_validator("surname")
    def validate_surname(cls, value: str):
        if not value in LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contain only letters."
            )
        return value
