import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.users.enums import UserRoles


class User(Base):
    """SQLAlchemy model representing a user in the system.

    Attributes:
        user_id (UUID): Primary key, unique identifier for the user.
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
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

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
