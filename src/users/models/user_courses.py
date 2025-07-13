import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import mapped_column, Mapped

from src.base.models import BaseTimeStampMixin, BaseUUIDMixin


class UserCourses(BaseUUIDMixin, BaseTimeStampMixin):
    __tablename__ = 'user_courses'

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        UUID(as_uuid=True),
        primary_key=True,

    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('courses.id', ondelete='CASCADE'),
        UUID(as_uuid=True),
        primary_key=True,
    )
