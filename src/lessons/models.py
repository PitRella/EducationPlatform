import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    Enum,
    ForeignKey,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import BaseTimeStampMixin, BaseUUIDMixin
from src.lessons.enums import LessonTypeEnum

if TYPE_CHECKING:
    from src.courses.models import Course


class Lesson(BaseUUIDMixin, BaseTimeStampMixin):
    """Class representing a lesson model in a learning platform.

    Attributes:
        id: Primary key (UUID).
        title: Lesson title (max 200 chars).
        slug: Unique lesson identifier (max 255 chars).
        description: Lesson description (max 512 chars).
        course: Related course object.
        course_id: Course foreign key (UUID).
        order_number: Order of a lesson within course.
        type: Lesson type (video/quiz/text/practice).
        video_url: Path or URL to video content.
        video_duration: Video length in seconds.
        materials: Additional lesson materials (JSON).
        quiz_data: Quiz content and settings (JSON).
        estimated_duration: Expected completion time in minutes.
        is_free: Whether a lesson is freely accessible.
        is_published: Whether a lesson is visible to users.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = 'lessons'
    # Main fields
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True, comment='A lesson title'
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment='Lesson slug',
    )
    description: Mapped[str] = mapped_column(
        String(512), nullable=False, comment='Course description'
    )
    # Attached fields
    course: Mapped['Course'] = relationship(
        back_populates='lessons',
        single_parent=True,
        uselist=False,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('courses.id', ondelete='CASCADE'),
        comment='Course ID',
    )
    # Meta info fields
    order_number: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        index=True,
        comment='Order of lesson in course',
    )
    type: Mapped[LessonTypeEnum] = mapped_column(
        Enum(LessonTypeEnum),
        nullable=False,
        comment='Lesson type',
    )
    video_url: Mapped[str] = mapped_column(
        String(512), nullable=True, comment='Path or URL to video'
    )
    video_duration: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=True,
        comment='Video duration in seconds',
    )
    materials: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=True,
        comment='Lesson materials',
    )
    quiz_data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=True,
        comment='Quiz data',
    )
    estimated_duration: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=True,
        comment='Estimated duration in minutes',
    )
    is_free: Mapped[bool] = mapped_column(
        Boolean,
        comment='Is lesson free',
        default=False,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        comment='Is lesson published',
        default=False,
    )

    __table_args__ = (UniqueConstraint('course_id', 'order_number'),)
