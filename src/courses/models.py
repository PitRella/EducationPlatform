import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.courses.enums import (
    AvailableLanguagesEnum,
    CourseLevelEnum,
    CurrencyEnum,
)
from src.database import Base


class Course(Base):
    """Class representing a course model in a platform.

    Attributes:
        id: Primary key.
        title: Course title (max 40 chars).
        description: Course description (max 512 chars).
        level: Course level (enum).
        logo: Path or URL to logo image.
        author_id: Author's user ID (UUID).
        author: User object (relationship).
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

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    # Main fields
    title: Mapped[str] = mapped_column(
        String(40), nullable=False, index=True, comment='A course title'
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
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        comment='Author ID',
    )
    author = relationship('User', back_populates='courses')
    is_active: Mapped[bool] = mapped_column(
        Boolean, comment='Course is active', server_default='false'
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
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now,
    )
