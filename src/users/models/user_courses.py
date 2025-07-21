import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.base.models import BaseTimeStampMixin, BaseUUIDMixin


class UserCourses(BaseUUIDMixin, BaseTimeStampMixin):
    """Represents the association between users and courses.

    Includes foreign keys to user and course, with cascade delete behavior.
    """

    __tablename__ = 'user_courses'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('courses.id', ondelete='CASCADE'),
        primary_key=True,
    )
