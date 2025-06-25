from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from src.users.enums import UserRoles
import uuid
from src.database import Base


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    @property
    def is_user_admin(self) -> bool:
        return UserRoles.ADMIN in self.roles

    @property
    def is_user_superadmin(self) -> bool:
        return UserRoles.SUPERADMIN in self.roles

    @property
    def is_user_in_admin_group(self) -> bool:
        return (
            UserRoles.ADMIN in self.roles or UserRoles.SUPERADMIN in self.roles
        )
