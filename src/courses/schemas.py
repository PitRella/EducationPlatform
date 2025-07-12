import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

from src.base.schemas import BaseSchema
from src.courses.enums import (
    AvailableLanguagesEnum,
    CourseLevelEnum,
    CurrencyEnum,
)


class _BaseCourseSchema(BaseModel):
    """Base course schema."""

    title: Annotated[str, Field(min_length=5, max_length=40)]
    description: Annotated[str, Field(min_length=20, max_length=512)]
    level: CourseLevelEnum
    logo: str
    price: Annotated[Decimal, Field(gt=0, le=100000)]

    currency: CurrencyEnum
    language: AvailableLanguagesEnum


class BaseCourseResponseSchema(_BaseCourseSchema, BaseSchema):
    """Base course response schema."""

    discount: int
    rating: int
    created_at: datetime
    updated_at: datetime
    id: uuid.UUID


class BaseCreateCourseSchema(_BaseCourseSchema):
    """Base course schema for creation."""

    user_id: uuid.UUID
