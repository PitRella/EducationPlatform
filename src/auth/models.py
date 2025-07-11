import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.database import Base


class RefreshToken(Base):
    """SQLAlchemy model representing a refresh token session.

    Attributes:
        id (int): Primary key identifier of the refresh session.
        refresh_token (uuid.UUID): Unique refresh token.
        expires_in (float): Expiration time (in seconds or timestamp).
        created_at (datetime): Timestamp when the refresh session was created.
        user_id (uuid.UUID): Foreign key referencing the associated user.

    """

    __tablename__ = 'refresh_session'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    refresh_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    expires_in: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey('users.id', ondelete='CASCADE'),
    )
