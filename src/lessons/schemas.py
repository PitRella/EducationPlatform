import uuid
from typing import Annotated, Any

from pydantic import BaseModel, Field

from src.base.schemas import BaseSchema
from src.lessons.enums import LessonTypeEnum


class CreateLessonRequestSchema(BaseModel):
    """Schema for creating a lesson."""

    title: Annotated[str, Field(min_length=5, max_length=200)]
    description: Annotated[str, Field(min_length=5, max_length=512)]
    order_number: Annotated[int, Field(ge=1, le=100)]
    type: LessonTypeEnum
    video_url: str | None = None
    video_duration: int | None = None
    materials: dict[str, Any] | None = None
    quiz_data: dict[str, Any] | None = None
    estimated_duration: int | None = None

class UpdateLessonRequestSchema(CreateLessonRequestSchema):
    """Schema for updating a lesson."""

class LessonResponseSchema(BaseSchema):
    """Schema for lesson response."""

    title: str
    slug: str
    description: str
    course_id: uuid.UUID
    order_number: int
    type: LessonTypeEnum
    video_url: str
    video_duration: int
    materials: dict[str, Any]
    quiz_data: dict[str, Any]
    estimated_duration: int
    is_free: bool
