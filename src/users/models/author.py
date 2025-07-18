import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import BaseTimeStampMixin, BaseUUIDMixin

if TYPE_CHECKING:
    from src.courses.models import Course
    from src.users.models import User


class Author(BaseUUIDMixin, BaseTimeStampMixin):
    """Courses author"""

    __tablename__ = 'authors'

    # Main fields
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        comment='User ID',
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='author',
        single_parent=True,
        uselist=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment='Author slug',
    )
    is_verified: Mapped[bool] = mapped_column(
        default=False, nullable=False, comment='Author is verified'
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(7, 2),
        default=0.0,
        nullable=False,
        comment='Author total balance',
    )
    courses: Mapped[set['Course']] = relationship(
        back_populates='author',
    )
    # Social network fields
    facebook_url: Mapped[str] = mapped_column(
        String(255), nullable=True, comment='Facebook URL'
    )
    linkedin_url: Mapped[str] = mapped_column(
        String(255), nullable=True, comment='LinkedIn URL'
    )

    # Education
    education: Mapped[str] = mapped_column(
        nullable=True, comment='Education info'
    )

    # Geo info
    country: Mapped[str] = mapped_column(
        String(100), nullable=True, comment='Country'
    )
    city: Mapped[str] = mapped_column(
        String(100), nullable=True, comment='City'
    )

    # Contacts
    phone: Mapped[str] = mapped_column(
        String(20), nullable=True, comment='Contact phone'
    )
    website: Mapped[str] = mapped_column(
        String(255), nullable=True, comment='Contact website'
    )

    __table_args__ = (UniqueConstraint('user_id'),)  # Be sure its o2o relation
