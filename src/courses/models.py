import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import BaseTimeStampMixin, BaseUUIDMixin
from src.courses.enums import (
    AvailableLanguagesEnum,
    CourseLevelEnum,
    CurrencyEnum,
)

if TYPE_CHECKING:
    from src.lessons.models import Lesson
    from src.users.models import Author, User


class Course(BaseUUIDMixin, BaseTimeStampMixin):
    """Class representing a course model in a platform.

    Attributes:
        id: Primary key.
        title: Course title (max 40 chars).
        description: Course description (max 512 chars).
        level: Course level (enum).
        logo: Path or URL to logo image.
        user_id: User ID (UUID).
        user: User object (relationship).
        is_active: Is the course active.
        rating: Course rating (decimal).
        price: Course price (decimal).
        discount: Discount percentage (int).
        currency: Course currency (enum).
        language: Course language (enum).
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = 'courses'

    slug: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    # Main fields
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True, comment='A course title'
    )
    description: Mapped[str] = mapped_column(
        String(512), nullable=False, comment='Course description'
    )
    level: Mapped[str] = mapped_column(
        Enum(CourseLevelEnum), nullable=False, comment='Course level'
    )
    logo: Mapped[str] = mapped_column(
        String(512), nullable=False, comment='Path or URL to logo image'
    )
    author: Mapped['Author'] = relationship(back_populates='courses')
    lessons: Mapped[list['Lesson']] = relationship(back_populates='course')
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('authors.id', ondelete='CASCADE'),
        comment='Author ID',
    )
    users: Mapped['User'] = relationship(
        secondary='user_courses', back_populates='purchased_courses'
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        comment='Course is active',
        default=False,
    )
    rating: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0.0, index=True, comment='Course rating'
    )

    # Price fields
    price: Mapped[Decimal] = mapped_column(
        Numeric(7, 2),
        nullable=False,
        comment='Course price',
    )
    discount: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default='0',
        comment='Course discount percentage',
    )
    currency: Mapped[str] = mapped_column(
        Enum(CurrencyEnum),
        nullable=False,
        comment='Course currency',
    )
    language: Mapped[str] = mapped_column(
        Enum(AvailableLanguagesEnum),
        nullable=False,
        comment='Course available languages',
    )
