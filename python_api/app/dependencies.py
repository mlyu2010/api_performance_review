"""
FastAPI Dependencies Module
===========================

This module provides dependency injection functions for FastAPI route handlers,
primarily focused on authentication and authorization.

Dependencies
-----------
The module exports the following dependencies for use with FastAPI's Depends():

- **get_current_user**: Extracts and validates JWT token, returns authenticated User

JWT Authentication Flow
----------------------
1. Extract Bearer token from Authorization header
2. Validate token signature and expiration using AuthService
3. Look up user in database by username from token payload
4. Verify user is active and not deleted
5. Return authenticated User instance

Usage
-----
In FastAPI route handlers:

    from fastapi import Depends
    from app.dependencies import get_current_user
    from app.models.user import User

    @router.get("/protected")
    async def protected_route(current_user: User = Depends(get_current_user)):
        return {"username": current_user.username}

Swagger UI Integration
---------------------
The HTTPBearer security scheme is configured to work seamlessly with
Swagger UI's "Authorize" button. Users can authenticate by:
1. Logging in via /api/login to get a token
2. Clicking "Authorize" in Swagger UI
3. Pasting the token (without "Bearer" prefix)

Error Handling
-------------
All authentication failures raise HTTPException with appropriate status codes:
- 401 UNAUTHORIZED: Missing token, invalid token, or inactive user
- Includes WWW-Authenticate header for proper HTTP authentication

Security Notes
-------------
- Tokens are verified for signature, expiration, and payload integrity
- User must be active (is_active=True) and not deleted (deleted_at=None)
- All authentication attempts are logged for security auditing
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.services.auth_service import AuthService
from app.models.user import User

logger = logging.getLogger(__name__)

# HTTPBearer security scheme for Swagger UI integration
security = HTTPBearer(
    auto_error=False,
    scheme_name="Bearer",
    description="Enter your JWT token (just the token, without 'Bearer' prefix)"
)


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """
    FastAPI dependency function to authenticate and retrieve the current user.

    This dependency extracts the JWT token from the Authorization header,
    validates it, and returns the authenticated User instance. It should be
    used with FastAPI's Depends() in route handlers that require authentication.

    Authentication Process:
    1. Extract Bearer token from Authorization header
    2. Verify token signature and expiration using AuthService
    3. Extract username from token payload
    4. Query database for user with matching username
    5. Verify user is active and not soft-deleted
    6. Return authenticated User instance

    Parameters
    ----------
    credentials : Optional[HTTPAuthorizationCredentials]
        JWT credentials extracted from Authorization header by HTTPBearer security
        scheme. Injected automatically by FastAPI's dependency injection.

    Returns
    -------
    User
        The authenticated User model instance with all user data

    Raises
    ------
    HTTPException (401 UNAUTHORIZED)
        - If Authorization header is missing or malformed
        - If token is invalid, expired, or has invalid signature
        - If user is not found in database
        - If user account is inactive (is_active=False)
        - If user account is soft-deleted (deleted_at is not None)

    Examples
    --------
    Use in a protected route:

        @router.get("/me")
        async def get_my_profile(current_user: User = Depends(get_current_user)):
            return {
                "username": current_user.username,
                "email": current_user.email
            }

    Notes
    -----
    - All authentication attempts are logged with username and status
    - Token validation includes signature, expiration, and payload checks
    - Only active, non-deleted users can authenticate
    - Returns full User model instance (password hash is excluded via PydanticMeta)
    """
    logger.info(f"get_current_user called, credentials: {credentials}")

    if not credentials:
        logger.warning("No credentials provided - Authorization header missing or malformed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or malformed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    logger.info(f"Token received (first 20 chars): {token[:20]}...")

    try:
        token_data = await AuthService.verify_token(token)
        logger.info(f"Token verified for username: {token_data.get('username')}")
    except HTTPException as e:
        logger.error(f"Token verification failed: {e.detail}")
        raise

    user = await User.filter(username=token_data["username"], deleted_at__isnull=True, is_active=True).first()
    if user is None:
        logger.warning(f"User not found or inactive: {token_data['username']}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"User authenticated successfully: {user.username}")
    return user
