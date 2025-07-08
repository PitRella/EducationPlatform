import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.courses.enums import (
    AvailableLanguagesEnum,
    CourseLevelEnum,
    CurrencyEnum,
)


class BaseCourseSchema(BaseModel):
    """Base course schema for creation."""

    title: Annotated[str, Field(min_length=5, max_length=40)]
    description: Annotated[str, Field(min_length=20, max_length=512)]
    level: CourseLevelEnum
    logo: str
    price: Annotated[Decimal, Field(gt=0, le=100000)]
    currency: CurrencyEnum
    language: AvailableLanguagesEnum

    model_config = ConfigDict(from_attributes=True)


class BaseCourseResponseSchema(BaseCourseSchema):
    """Base course response schema."""

    id: uuid.UUID


class CreateCourseRequestSchema(BaseCourseSchema):
    """Course creation request schema."""

    author_id: uuid.UUID


class CreateCourseResponseSchema(BaseCourseResponseSchema):
    """Course creation response schema."""


class GetCourseResponseSchema(BaseCourseResponseSchema):
    """Course get response schema."""
