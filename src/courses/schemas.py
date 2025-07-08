import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.courses.enums import (
    AvailableLanguagesEnum,
    CourseLevelEnum,
    CurrencyEnum,
)


class BaseCourseResponseSchema(BaseModel):
    """Base course response schema."""

    id: uuid.UUID
    title: Annotated[str, Field(min_length=5, max_length=40)]
    description: Annotated[str, Field(min_length=20, max_length=512)]
    level: CourseLevelEnum
    logo: str
    price: Annotated[Decimal, Field(gt=0, le=100000)]
    currency: CurrencyEnum
    language: AvailableLanguagesEnum

    model_config = ConfigDict(from_attributes=True)


class BaseCreateCourseSchema(BaseModel):
    """Base course schema for creation."""

    author_id: uuid.UUID
    title: Annotated[str, Field(min_length=5, max_length=40)]
    description: Annotated[str, Field(min_length=20, max_length=512)]
    level: CourseLevelEnum
    logo: str
    price: Annotated[Decimal, Field(gt=0, le=100000)]
    currency: CurrencyEnum
    language: AvailableLanguagesEnum

    model_config = ConfigDict(from_attributes=True)
