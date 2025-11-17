"""
User model for authentication and user management.
"""
from sqlalchemy import Boolean, String, Column
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.core.security import hash_password, verify_password


class User(Base):
    """
    User model for storing user account information.

    Inherits id, created_at, updated_at from Base class.
    """
    __tablename__ = "users"

    # User credentials
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique username for login"
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address"
    )
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password (bcrypt)"
    )

    # User status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active"
    )
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user has superuser privileges"
    )

    # Relationships (будут добавлены в задачах #6, #7)
    # tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    # categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """
        Hash and set user password.

        Args:
            password: Plain text password

        Example:
            >>> user = User(username="john", email="john@example.com")
            >>> user.set_password("mypassword123")
            >>> print(user.password_hash)
            $2b$12$...
        """
        self.password_hash = hash_password(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise

        Example:
            >>> user.set_password("mypassword123")
            >>> user.verify_password("mypassword123")
            True
            >>> user.verify_password("wrongpassword")
            False
        """
        return verify_password(password, self.password_hash)

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"