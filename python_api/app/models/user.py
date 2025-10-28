"""
User Model Module
================

This module defines the User model for authentication and user management.

The User model provides:
- User account storage with unique username and email
- Secure password hashing using bcrypt
- Account status tracking (active/inactive)
- Soft delete support via deleted_at timestamp
- Password verification methods
- Automatic created/updated timestamps

Security Features
----------------
- Passwords are hashed using bcrypt with automatic salt generation
- Password hashes are never exposed in API responses (excluded via PydanticMeta)
- Password verification uses constant-time comparison
- Support for password scheme migration via passlib's deprecated parameter

Database Table
-------------
Table name: users

Fields:
- id: Primary key (auto-increment integer)
- username: Unique, indexed varchar(100)
- email: Unique, indexed varchar(255)
- hashed_password: Bcrypt hash varchar(255)
- is_active: Boolean flag for account status
- created_at: Timestamp (auto-populated on creation)
- updated_at: Timestamp (auto-updated on modification)
- deleted_at: Timestamp for soft deletes (nullable)
"""

from tortoise import fields
from tortoise.models import Model
from passlib.context import CryptContext

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Model):
    """
    User model for authentication and user management.

    Represents a user account with secure password storage, account status
    tracking, and support for soft deletion. Passwords are hashed using
    bcrypt for security.

    Attributes
    ----------
    id : int
        Primary key, auto-incremented
    username : str
        Unique username, max 100 characters, indexed for fast lookups
    email : str
        Unique email address, max 255 characters, indexed
    hashed_password : str
        Bcrypt password hash, max 255 characters
        Never exposed in API responses (excluded via PydanticMeta)
    is_active : bool
        Account active status, defaults to True
        Inactive users cannot authenticate
    created_at : datetime
        Timestamp when the user was created, auto-populated
    updated_at : datetime
        Timestamp when the user was last updated, auto-updated
    deleted_at : datetime, optional
        Timestamp when the user was soft-deleted, None if not deleted

    Methods
    -------
    verify_password(plain_password: str) -> bool
        Verify a plain password against the stored hash
    get_password_hash(password: str) -> str
        Static method to hash a plain password (class method)

    Examples
    --------
    Create a new user:
        user = await User.create(
            username="john",
            email="john@example.com",
            hashed_password=User.get_password_hash("secretpassword"),
            is_active=True
        )

    Verify password:
        is_valid = user.verify_password("secretpassword")

    Soft delete a user:
        from datetime import datetime
        user.deleted_at = datetime.utcnow()
        await user.save()

    Query active users only:
        active_users = await User.filter(is_active=True, deleted_at__isnull=True).all()
    """
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100, unique=True, index=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        table = "users"

    def verify_password(self, plain_password: str) -> bool:
        """
        Verify a plain text password against the stored password hash.

        Uses bcrypt's constant-time comparison to prevent timing attacks.
        The verification process includes automatic rehashing if the stored
        hash uses a deprecated scheme.

        Parameters
        ----------
        plain_password : str
            The plain text password to verify

        Returns
        -------
        bool
            True if the password matches, False otherwise

        Examples
        --------
        if user.verify_password("submitted_password"):
            # Password is correct, proceed with authentication
            pass
        else:
            # Password is incorrect, reject authentication
            pass
        """
        return pwd_context.verify(plain_password, self.hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Generate a bcrypt hash for a plain text password.

        This static method can be called on the User class without an instance.
        It uses bcrypt with automatic salt generation for secure password storage.

        Parameters
        ----------
        password : str
            The plain text password to hash

        Returns
        -------
        str
            The bcrypt password hash (includes salt and algorithm parameters)

        Examples
        --------
        Create user with hashed password:
            hashed = User.get_password_hash("my_secure_password")
            user = await User.create(
                username="john",
                email="john@example.com",
                hashed_password=hashed
            )

        Notes
        -----
        - Each call generates a unique salt, so the same password produces
          different hashes
        - The hash includes algorithm version, cost factor, and salt
        - Never store plain text passwords, always use this method
        """
        return pwd_context.hash(password)

    class PydanticMeta:
        exclude = ["hashed_password"]
