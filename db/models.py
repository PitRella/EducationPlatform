from sqlalchemy import String, Boolean
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, \
    DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               primary_key=True,
                                               default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
