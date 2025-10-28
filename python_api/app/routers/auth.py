"""
Authentication Router Module
===========================

This module provides authentication endpoints for the Agents & Tasks API.

Endpoints
--------
POST /api/login
    Authenticate user with username and password, returns JWT access token

Authentication Flow
------------------
1. Client sends POST request to /api/login with username and password
2. Server validates credentials against database
3. If valid, server generates JWT token with user info and expiration
4. Client receives token and includes it in subsequent requests
5. Protected endpoints verify token using get_current_user dependency

JWT Token
---------
The JWT token includes:
- sub: Username (subject)
- exp: Expiration timestamp (UTC)
- Signed with SECRET_KEY using HS256 algorithm

Token expires after ACCESS_TOKEN_EXPIRE_MINUTES (configurable in settings).

Usage in Swagger UI
------------------
1. Call POST /api/login with valid credentials
2. Copy the access_token value from response (without quotes)
3. Click "Authorize" button (🔓) at top right
4. Paste token in "Value" field (do NOT include "Bearer")
5. Click "Authorize" then "Close"
6. All protected endpoints are now accessible

Usage in Client Applications
----------------------------
Include token in Authorization header:
    Authorization: Bearer <access_token>

Example with curl:
    curl -X GET "http://localhost:8000/api/agents" \\
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

Example with Python requests:
    import requests

    # Login
    response = requests.post(
        "http://localhost:8000/api/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]

    # Use token
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8000/api/agents", headers=headers)

Error Responses
--------------
404 NOT FOUND:
    - Incorrect username or password
    - User account not found

401 UNAUTHORIZED:
    - Token expired or invalid
    - Missing Authorization header

Security Notes
-------------
- Passwords are hashed using bcrypt before storage
- Tokens are signed and cannot be tampered with
- Tokens expire and must be refreshed by re-authenticating
- Never store passwords in plain text
- Use HTTPS in production to protect tokens in transit
"""

from fastapi import APIRouter, HTTPException, status
from datetime import timedelta

from fastapi.security import OAuth2PasswordBearer

from app.schemas.auth import LoginRequest, Token


# OAuth2 password bearer scheme for Swagger UI integration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=Token, summary="Authenticate user and get JWT token")
async def login(login_data: LoginRequest):
    """
    Authenticate a user with username and password.

    Returns a JWT token that must be used for subsequent API calls.

    **Request Body:**
    - username: User's username
    - password: User's password

    **Returns:**
    - access_token: JWT token
    - token_type: Token type (bearer)

    **Errors:**
    - 404: User not found or invalid credentials
    """
    user = await AuthService.authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
