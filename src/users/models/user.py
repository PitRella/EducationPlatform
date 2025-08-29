from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import BaseTimeStampMixin, BaseUUIDMixin
from src.payment.models import Payment
from src.users.enums import UserRole

if TYPE_CHECKING:
    from src.courses.models import Course
    from src.users.models import Author


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
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        server_default='USER',
    )
    author: Mapped[Optional['Author']] = relationship(
        'Author', back_populates='user', uselist=False
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )
    purchased_courses: Mapped[list['Course']] = relationship(
        'Course', secondary='user_courses', back_populates='users'
    )
    payments: Mapped[list['Payment']] = relationship(back_populates='user')

    @property
    def is_user_admin(self) -> bool:
        """Check if a user is admin or not."""
        return self.role == UserRole.ADMIN

    @property
    def is_user_superadmin(self) -> bool:
        """Check if a user is superadmin or not."""
        return self.role == UserRole.SUPERADMIN

    @property
    def is_user_in_admin_group(self) -> bool:
        """Check if user in an admin group or not."""
        return self.is_user_admin or self.is_user_superadmin
