import uuid

from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, Enum, String, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.base.models import BaseUUIDMixin, BaseTimeStampMixin

from src.users.enums import UserRoles

if TYPE_CHECKING:
    from src.author.model import Author
    from src.courses.models import Course


class User(BaseUUIDMixin, BaseTimeStampMixin):
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
        is_user_admin (bool): Check if the user has an admin role.
        is_user_superadmin (bool): Check if the user has a superadmin role.
        is_user_in_admin_group (bool): Check if a user has either admin
         or superadmin role.

    """

    __tablename__ = 'users'

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
    roles: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles),
        nullable=False,
        server_default='USER',
    )
    author: Mapped[Optional["Author"]] = relationship(
        'Author',
        back_populates='user',
        uselist=False
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )
    purchased_courses: Mapped["Course"] = relationship(
        'Course',
        secondary='user_courses',
        back_populates='users'
    )

    @property
    def is_user_admin(self) -> bool:
        """Check if a user is admin or not."""
        return self.roles == UserRoles.ADMIN

    @property
    def is_user_superadmin(self) -> bool:
        """Check if a user is superadmin or not."""
        return self.roles == UserRoles.SUPERADMIN

    @property
    def is_user_in_admin_group(self) -> bool:
        """Check if user in an admin group or not."""
        return self.is_user_admin or self.is_user_superadmin
