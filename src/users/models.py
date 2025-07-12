import uuid

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.users.enums import UserRoles


class User(Base):
    """SQLAlchemy model representing a user in the system.

    Attributes:
        id (UUID): Primary key, unique identifier for the user.
        name (str): User's first name.
        surname (str): User's last name.
        email (str): User's email an address must be unique.
        password (str): Hashed password for user authentication.
        roles (List[str]): List of roles assigned to the user.
        is_active (bool): Flag indicating if the user account is active.

    Properties:
        is_user_admin (bool): Check if user has an admin role.
        is_user_superadmin (bool): Check if user has a superadmin role.
        is_user_in_admin_group (bool): Check if a user has either admin
         or superadmin role.

    """

    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    surname: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    roles: Mapped[list[str]] = mapped_column(
        Enum(UserRoles),
        nullable=False,
        server_default='USER',
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean(),
        default=True,
    )
    courses = relationship('Course', back_populates='user', lazy='joined')

    @property
    def is_user_admin(self) -> bool:
        """Check if a user is admin or not."""
        return UserRoles.ADMIN in self.roles

    @property
    def is_user_superadmin(self) -> bool:
        """Check if a user is superadmin or not."""
        return UserRoles.SUPERADMIN in self.roles

    @property
    def is_user_in_admin_group(self) -> bool:
        """Check if user in an admin group or not."""
        return (
            UserRoles.ADMIN in self.roles or UserRoles.SUPERADMIN in self.roles
        )
