"""
Authentication Service Module
=============================

This module provides authentication and JWT token management services.

The AuthService class handles:
- JWT token creation with expiration
- User authentication (username + password)
- JWT token verification and validation

JWT Token Structure
------------------
Tokens contain:
- sub: Username (subject claim)
- exp: Expiration timestamp (UTC)
- Signature: HMAC-SHA256 signed with SECRET_KEY

Token Lifecycle
--------------
1. Create: POST /api/login with credentials
2. Use: Include in Authorization header for protected endpoints
3. Expire: Token expires after ACCESS_TOKEN_EXPIRE_MINUTES
4. Refresh: Re-authenticate to get new token

Security Features
----------------
- Passwords verified using bcrypt (constant-time comparison)
- Tokens signed with SECRET_KEY (prevents tampering)
- Token expiration enforced
- Only active, non-deleted users can authenticate
- All operations logged for security auditing

Dependencies
-----------
- python-jose: JWT encoding/decoding
- passlib: Password hashing verification
- Tortoise ORM: User database queries

Configuration
------------
Settings from app.config:
- SECRET_KEY: JWT signing key (must be strong in production)
- ALGORITHM: JWT signing algorithm (HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES: Token lifetime

Usage
-----
In routers:
    from app.services.auth_service import AuthService

    # Authenticate user
    user = await AuthService.authenticate_user(username, password)

    # Create token
    token = AuthService.create_access_token(data={"sub": user.username})

    # Verify token
    token_data = await AuthService.verify_token(token)

Error Handling
-------------
All authentication failures raise HTTPException with appropriate status:
- 401 UNAUTHORIZED: Invalid credentials, expired token, invalid signature
- Includes WWW-Authenticate header for proper HTTP auth flow

Security Notes
-------------
- Never log passwords or tokens (only first 20 chars for debugging)
- Use HTTPS in production to protect tokens in transit
- Rotate SECRET_KEY periodically
- Consider shorter token lifetimes for sensitive applications
- Implement token refresh mechanism for better UX
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
import logging

from app.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service providing JWT and user authentication operations.

    This service class contains static methods for:
    - Creating JWT access tokens
    - Authenticating users with username/password
    - Verifying and decoding JWT tokens

    All methods are static as they don't require instance state.

    Methods
    -------
    create_access_token(data, expires_delta)
        Generate JWT access token with user data and expiration

    authenticate_user(username, password)
        Verify user credentials and return User instance

    verify_token(token)
        Decode and validate JWT token, return username
    """
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """
        Create a JWT access token with user data and expiration.

        Generates a signed JWT token containing the provided data plus
        an expiration timestamp. The token is signed with SECRET_KEY
        using the configured algorithm (HS256).

        Parameters
        ----------
        data : dict
            Data to encode in the token (typically {"sub": username})
            The 'sub' (subject) claim should contain the username
        expires_delta : timedelta, optional
            Custom token expiration time
            If not provided, uses ACCESS_TOKEN_EXPIRE_MINUTES from settings

        Returns
        -------
        str
            Encoded JWT token string

        Examples
        --------
        Create token with default expiration:
            token = AuthService.create_access_token(data={"sub": "admin"})

        Create token with custom expiration (1 hour):
            from datetime import timedelta
            token = AuthService.create_access_token(
                data={"sub": "admin"},
                expires_delta=timedelta(hours=1)
            )

        Notes
        -----
        - Token includes 'exp' (expiration) claim automatically
        - Token is signed and cannot be tampered with
        - Token should be transmitted over HTTPS only
        - Client should include token in Authorization header:
          Authorization: Bearer <token>
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.

        Looks up user by username and verifies password hash using bcrypt.
        Only returns user if account is active and not soft-deleted.

        Parameters
        ----------
        username : str
            User's username
        password : str
            User's plain text password

        Returns
        -------
        User | None
            User instance if authentication successful, None otherwise

        Examples
        --------
        user = await AuthService.authenticate_user("admin", "admin123")
        if user:
            # Authentication successful
            token = AuthService.create_access_token(data={"sub": user.username})
        else:
            # Authentication failed
            raise HTTPException(status_code=401, detail="Invalid credentials")

        Notes
        -----
        Returns None if:
        - Username not found
        - User account is inactive (is_active=False)
        - User account is soft-deleted (deleted_at is not null)
        - Password verification fails

        Password verification uses bcrypt with constant-time comparison
        to prevent timing attacks.
        """
        user = await User.filter(username=username, deleted_at__isnull=True, is_active=True).first()
        if not user:
            return None
        if not user.verify_password(password):
            return None
        return user

    @staticmethod
    async def verify_token(token: str) -> dict:
        """
        Verify and decode JWT access token.

        Validates token signature, expiration, and structure.
        Extracts username from 'sub' (subject) claim.

        Parameters
        ----------
        token : str
            JWT token string (without 'Bearer ' prefix)

        Returns
        -------
        dict
            Dictionary containing {"username": str} extracted from token

        Raises
        ------
        HTTPException (401 UNAUTHORIZED)
            - Token signature is invalid
            - Token has expired
            - Token structure is malformed
            - Token missing 'sub' (username) claim

        Examples
        --------
        try:
            token_data = await AuthService.verify_token(token)
            username = token_data["username"]
            # Token is valid, proceed with request
        except HTTPException:
            # Token is invalid, reject request
            pass

        Notes
        -----
        - Logs token validation for security auditing
        - Only logs first 20 characters of token (security)
        - Includes detailed error messages for debugging
        - Raises HTTPException with WWW-Authenticate header
        - All JWT errors (expired, invalid signature, etc.) result in 401
        """
        try:
            logger.info(f"Verifying token (first 20 chars): {token[:20]}...")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            logger.info(f"Token decoded successfully, payload: {payload}")
            username: str = payload.get("sub")
            if username is None:
                logger.error("Token payload missing 'sub' field")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials - missing username",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            logger.info(f"Token valid for username: {username}")
            return {"username": username}
        except JWTError as e:
            logger.error(f"JWT decode error: {type(e).__name__} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
