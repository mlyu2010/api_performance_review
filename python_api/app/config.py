"""
Application Configuration Module
================================

This module manages all configuration settings for the Agents & Tasks API
using Pydantic Settings for validation and environment variable loading.

Configuration Sources
--------------------
Settings are loaded from multiple sources in order of precedence:
1. Environment variables
2. .env file (if present)
3. Default values defined in the Settings class

Configuration Categories
-----------------------
- **Environment**: Deployment environment (development/staging/production)
- **Database**: PostgreSQL connection and pool settings
- **JWT**: Secret key and token expiration settings
- **API**: API versioning and project metadata
- **CORS**: Cross-Origin Resource Sharing configuration
- **Rate Limiting**: API rate limit settings
- **Logging**: Log level and format configuration
- **Server**: Worker and connection settings for production

Production Validation
--------------------
The module includes critical security validations for production deployments:
- SECRET_KEY must be changed from default value
- SECRET_KEY must be at least 32 characters
- ALLOWED_ORIGINS must be restricted (not wildcard)
- Database credentials should not use default values

These validations run automatically on startup and will prevent the application
from starting if any critical security settings are misconfigured.

Usage
-----
Import the singleton settings instance:
    from app.config import settings

    database_url = settings.DATABASE_URL
    secret_key = settings.SECRET_KEY

Environment Variables
--------------------
Create a .env file in the project root (see .env.example):
    ENVIRONMENT=production
    DATABASE_URL=postgres://user:pass@host:5432/dbname
    SECRET_KEY=your-super-secret-key-at-least-32-chars
    ALLOWED_ORIGINS=https://example.com,https://app.example.com

Security Notes
-------------
- NEVER commit .env files to version control
- ALWAYS change SECRET_KEY in production
- ALWAYS restrict ALLOWED_ORIGINS in production
- Use strong database credentials in production
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
import sys


class Settings(BaseSettings):
    """
    Application settings with validation and environment variable loading.

    This class defines all configuration parameters for the API with default
    values suitable for local development. Production deployments should
    override these values using environment variables or a .env file.

    Attributes
    ----------
    ENVIRONMENT : str
        Deployment environment (development, staging, production)
        Default: 'development'

    DATABASE_URL : str
        PostgreSQL connection string
        Format: postgres://user:password@host:port/database
        Default: Local development database

    DATABASE_POOL_SIZE : int
        Maximum number of database connections in the pool
        Default: 20

    DATABASE_MAX_OVERFLOW : int
        Maximum overflow connections beyond pool_size
        Default: 40

    SECRET_KEY : str
        Secret key for JWT token signing (MUST be changed in production)
        Default: Development-only insecure key

    ALGORITHM : str
        JWT signing algorithm
        Default: 'HS256'

    ACCESS_TOKEN_EXPIRE_MINUTES : int
        JWT token expiration time in minutes
        Default: 30

    API_V1_STR : str
        API version prefix for routes
        Default: '/api'

    PROJECT_NAME : str
        Project display name
        Default: 'Agents & Tasks API'

    ALLOWED_ORIGINS : str
        Comma-separated list of allowed CORS origins or '*' for all
        Default: '*' (development only - must be restricted in production)

    RATE_LIMIT_CALLS : int
        Maximum API calls per time window
        Default: 100

    RATE_LIMIT_WINDOW : int
        Rate limit time window in seconds
        Default: 60

    LOG_LEVEL : str
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        Default: 'INFO'

    LOG_FORMAT : str
        Log output format ('json' or 'text')
        Default: 'json'

    WORKERS : int
        Number of worker processes for production server
        Default: 4

    MAX_CONNECTIONS : int
        Maximum concurrent connections
        Default: 1000

    KEEPALIVE : int
        Keep-alive timeout in seconds
        Default: 5

    Methods
    -------
    validate_production_settings()
        Validates critical security settings for production deployment
    get_allowed_origins_list()
        Parses ALLOWED_ORIGINS string into a list
    """
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database
    DATABASE_URL: str = "postgres://postgres:postgres@db:5432/agents_tasks_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # JWT - CRITICAL: Must be strong in production
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Agents & Tasks API"

    # CORS - CRITICAL: Restrict in production
    ALLOWED_ORIGINS: str = "*"  # Comma-separated list of allowed origins

    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "json"  # json or text

    # Server
    WORKERS: int = 4
    MAX_CONNECTIONS: int = 1000
    KEEPALIVE: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_production_settings(self):
        """
        Validate critical security settings for production deployment.

        Performs comprehensive security checks when ENVIRONMENT is set to 'production':
        1. Ensures SECRET_KEY has been changed from default value
        2. Validates SECRET_KEY is at least 32 characters (strong enough)
        3. Verifies ALLOWED_ORIGINS is restricted (not wildcard '*')
        4. Checks database credentials are not using defaults

        If any validation fails, errors are printed to stderr and the
        application exits with status code 1, preventing insecure deployment.

        Raises
        ------
        SystemExit
            If any production validation check fails

        Notes
        -----
        This method is called automatically during settings initialization.
        For non-production environments, validation is skipped.
        """
        if self.ENVIRONMENT == "production":
            errors = []

            # Check SECRET_KEY is not default
            if self.SECRET_KEY == "your-secret-key-change-this-in-production":
                errors.append("SECRET_KEY must be changed from default value in production")

            # Check SECRET_KEY is strong enough
            if len(self.SECRET_KEY) < 32:
                errors.append("SECRET_KEY must be at least 32 characters long in production")

            # Check CORS is restricted
            if self.ALLOWED_ORIGINS == "*":
                errors.append("ALLOWED_ORIGINS must be restricted (not '*') in production")

            # Check database URL doesn't use default credentials
            if "postgres:postgres" in self.DATABASE_URL:
                errors.append("DATABASE_URL should not use default postgres credentials in production")

            if errors:
                print("PRODUCTION CONFIGURATION ERRORS:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                sys.exit(1)

    def get_allowed_origins_list(self) -> list:
        """
        Parse ALLOWED_ORIGINS configuration string into a list.

        Converts the comma-separated ALLOWED_ORIGINS string into a list
        of origin URLs for CORS middleware configuration. Handles both
        wildcard ('*') and specific origin lists.

        Returns
        -------
        list
            List containing either ['*'] for all origins, or a list of
            specific origin URLs (e.g., ['https://example.com', 'https://app.example.com'])

        Examples
        --------
        With wildcard:
            ALLOWED_ORIGINS = "*"
            result = ["*"]

        With specific origins:
            ALLOWED_ORIGINS = "https://example.com,https://app.example.com"
            result = ["https://example.com", "https://app.example.com"]
        """
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings singleton instance.

    Creates and returns a cached Settings instance. The @lru_cache decorator
    ensures only one Settings instance is created, making this function a
    singleton factory.

    The function also triggers production settings validation, ensuring
    security requirements are met before the application starts.

    Returns
    -------
    Settings
        The application settings singleton instance

    Raises
    ------
    SystemExit
        If production validation fails (via validate_production_settings)

    Notes
    -----
    This function is called once at module import time to create the
    global 'settings' instance. Subsequent calls return the cached instance.
    """
    settings = Settings()
    settings.validate_production_settings()
    return settings


settings = get_settings()
