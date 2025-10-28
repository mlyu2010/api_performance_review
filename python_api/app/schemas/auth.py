"""
Authentication Schemas Module
============================

This module defines Pydantic schemas for authentication-related requests and responses.

Schemas
-------
LoginRequest : BaseModel
    User credentials for authentication (username + password)

Token : BaseModel
    JWT token response after successful login

TokenData : BaseModel
    Decoded JWT token payload data

UserCreate : BaseModel
    User registration request (not currently used)

UserResponse : BaseModel
    User details response (not currently used)

Authentication Flow
------------------
1. Client sends LoginRequest to POST /api/login
2. Server validates credentials and generates JWT
3. Server responds with Token containing access_token
4. Client includes token in subsequent requests
5. Server validates token and extracts TokenData

Security Notes
-------------
- Passwords are never returned in responses
- LoginRequest passwords are immediately hashed
- Tokens expire after configured time period
- Token validation checks signature and expiration

Usage Examples
-------------
Login request:
    POST /api/login
    {
        "username": "admin",
        "password": "admin123"
    }

Token response:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }

Using the token:
    GET /api/agents
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Login request schema for user authentication.

    Attributes
    ----------
    username : str
        User's unique username
    password : str
        User's plain text password (will be verified against hashed password)

    Examples
    --------
    {
        "username": "admin",
        "password": "admin123"
    }

    Notes
    -----
    The password is transmitted in plain text, so HTTPS should always be
    used in production to protect credentials in transit.
    """
    username: str
    password: str


class Token(BaseModel):
    """
    JWT token response schema.

    Returned after successful authentication via POST /api/login.

    Attributes
    ----------
    access_token : str
        The JWT access token string
        Contains encoded user information and expiration
    token_type : str
        Token type identifier, always "bearer" for JWT
        Default: "bearer"

    Examples
    --------
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY4...",
        "token_type": "bearer"
    }

    Notes
    -----
    The access_token should be included in the Authorization header
    for subsequent API requests:
        Authorization: Bearer <access_token>
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Decoded JWT token payload schema.

    Represents the data extracted from a validated JWT token.
    Used internally by authentication services.

    Attributes
    ----------
    username : str | None
        Username extracted from token's 'sub' (subject) claim
        None if token is invalid or missing subject

    Notes
    -----
    This schema is used internally and not exposed in API responses.
    The JWT payload also includes 'exp' (expiration) which is validated
    but not included in this schema.
    """
    username: str | None = None


class UserCreate(BaseModel):
    """
    User registration request schema.

    Currently not used - user creation is handled by database initialization.
    Reserved for future user registration endpoint.

    Attributes
    ----------
    username : str
        Desired unique username
    email : EmailStr
        Valid email address (validated by Pydantic)
    password : str
        Plain text password (will be hashed before storage)

    Examples
    --------
    {
        "username": "newuser",
        "email": "user@example.com",
        "password": "SecurePassword123!"
    }

    Notes
    -----
    When implementing user registration:
    - Validate username uniqueness
    - Validate email uniqueness
    - Hash password before storing
    - Consider password strength requirements
    """
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    User details response schema.

    Currently not used - reserved for user profile endpoints.

    Attributes
    ----------
    id : int
        User's unique identifier
    username : str
        User's username
    email : str
        User's email address
    is_active : bool
        Whether the user account is active

    Examples
    --------
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_active": true
    }

    Notes
    -----
    - Password hash is never included in responses
    - deleted_at timestamp is not exposed
    - Use from_attributes=True to convert from ORM models
    """
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True
