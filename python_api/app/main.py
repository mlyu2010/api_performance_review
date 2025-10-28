"""
Agents & Tasks API - Main Application Module
============================================

This is the main entry point for the Agents & Tasks REST API built with FastAPI.
The application provides comprehensive endpoints for managing AI agents, tasks,
and their executions with JWT-based authentication.

Key Features
-----------
- **JWT Authentication**: Secure user authentication with token-based access
- **Agent Management**: CRUD operations for AI agents
- **Task Management**: Create and manage tasks, assign to agents
- **Execution Tracking**: Monitor and track task execution status
- **Rate Limiting**: Configurable rate limiting middleware
- **Health Checks**: Readiness, liveness, and basic health endpoints
- **CORS Support**: Configurable CORS for frontend integration
- **Structured Logging**: JSON or text-based logging with environment-specific levels
- **Database Integration**: Tortoise ORM with PostgreSQL

Architecture
-----------
The application follows a layered architecture:
- **Routers**: Handle HTTP requests and responses (app/routers/)
- **Services**: Business logic and data operations (app/services/)
- **Models**: Database models using Tortoise ORM (app/models/)
- **Schemas**: Pydantic models for request/response validation (app/schemas/)
- **Middleware**: Request processing, rate limiting (app/middleware/)

Configuration
------------
Configuration is managed through environment variables and loaded via
app.config.Settings. See .env.example for available options.

Startup
-------
The application uses an async lifespan context manager to:
1. Initialize database connections on startup
2. Generate database schemas if needed
3. Gracefully close connections on shutdown

Logging
-------
Supports two logging formats:
- **JSON**: Structured logging for production (easier parsing/analysis)
- **Text**: Human-readable format for development

Log levels can be configured per environment (DEBUG, INFO, WARNING, ERROR, CRITICAL).

Health Checks
------------
Three health check endpoints for different monitoring needs:
- **/health**: Basic health check (service running)
- **/health/ready**: Readiness check with database connectivity
- **/health/live**: Liveness probe for orchestration platforms

API Documentation
----------------
Interactive API documentation available at:
- Swagger UI: /docs
- ReDoc: /redoc
- OpenAPI JSON: /openapi.json

Usage
-----
Start the development server:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

For production deployment:
    gunicorn app.main:app -c gunicorn_conf.py

Environment Variables
--------------------
See app/config.py for complete list. Key variables:
- DATABASE_URL: PostgreSQL connection string
- SECRET_KEY: JWT secret (must be changed in production)
- ENVIRONMENT: development, staging, or production
- LOG_LEVEL: Logging verbosity
- ALLOWED_ORIGINS: CORS allowed origins

Security Notes
-------------
- Change SECRET_KEY in production (validated on startup)
- Restrict ALLOWED_ORIGINS in production (validated on startup)
- Use strong database credentials (validated on startup)
- Rate limiting is enabled by default
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from tortoise import Tortoise
import logging
import logging.config
import time
import sys
import json
from datetime import datetime

from app.config import settings
from app.middleware.rate_limiter import RateLimitMiddleware
from app.routers import auth, agents, tasks, executions


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Formats log records as JSON objects with standardized fields including
    timestamp, level, logger name, message, module, function, and line number.
    Also includes exception information if present.

    This formatter is useful for production environments where logs are
    processed by log aggregation tools (e.g., ELK stack, CloudWatch).

    Attributes
    ----------
    The formatter creates log entries with the following JSON fields:
    - timestamp: ISO 8601 formatted UTC timestamp
    - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - logger: Name of the logger
    - message: Log message
    - module: Module name where log was generated
    - function: Function name where log was generated
    - line: Line number where log was generated
    - exception: Stack trace (only if exception occurred)
    """
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging():
    """
    Configure application logging based on environment settings.

    Sets up logging with either JSON or text formatting based on the
    LOG_FORMAT configuration. Configures log levels and reduces noise
    from third-party libraries in production.

    The function configures:
    - Root logger with appropriate log level
    - Console handler (stdout) with selected formatter
    - Library-specific log levels (reduced verbosity in production)

    Configuration is read from app.config.settings:
    - LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, or CRITICAL
    - LOG_FORMAT: 'json' for structured logs, 'text' for human-readable
    - ENVIRONMENT: Used to determine library log verbosity

    Notes
    -----
    In production environment, third-party library logs (uvicorn, tortoise)
    are set to WARNING level to reduce noise.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.LOG_FORMAT == "json":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Reduce noise from third-party libraries in production
    if settings.ENVIRONMENT == "production":
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("tortoise").setLevel(logging.WARNING)


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for application lifespan events.

    Handles startup and shutdown operations for the FastAPI application:

    Startup:
    - Initialize Tortoise ORM database connection
    - Generate database schemas if they don't exist
    - Log successful initialization

    Shutdown:
    - Gracefully close all database connections
    - Log shutdown completion

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance

    Yields
    ------
    None
        Control is yielded to the application after startup,
        then cleanup occurs after the yield when shutting down

    Notes
    -----
    This context manager ensures proper resource cleanup even if
    the application encounters errors during execution.
    """
    # Startup
    logger.info("Starting application...")
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await Tortoise.close_connections()
    logger.info("Database connections closed")


app = FastAPI(
    title="Agents & Tasks API",
    description="""
    REST API for Managing Agents, Tasks, and Executions

    This API provides comprehensive endpoints for:

    * **Authentication**: User registration, login, and JWT token management
    * **Agents**: Create, read, update, and delete AI agents
    * **Tasks**: Manage tasks and assign them to agents
    * **Executions**: Track and monitor task executions

    ### Authentication

    Most endpoints require JWT authentication. To use protected endpoints:

    1. Login via `/api/login` with username: `admin` and password: `admin123`
    2. Copy the **access_token** value from the response (without quotes)
    3. Click the **Authorize** button (🔓) at the top right
    4. Paste the token in the "Value" field (do NOT include "Bearer" - just the token)
    5. Click **Authorize** and then **Close**
    6. Now you can access all protected endpoints!

    **Note:** The token expires after 60 minutes. If you get 401 errors, login again to get a new token.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    HTTP middleware for request/response logging with performance tracking.

    Logs all HTTP requests and responses with timing information. The verbosity
    and detail level adjusts based on the environment (production vs development).

    Features:
    - Request method and path logging
    - Response time tracking
    - Slow request warnings (>1 second)
    - Health check endpoint filtering (reduces noise)
    - Environment-aware verbosity (minimal in production)

    Parameters
    ----------
    request : Request
        The incoming HTTP request
    call_next : Callable
        The next middleware or route handler in the chain

    Returns
    -------
    Response
        The HTTP response from the route handler

    Notes
    -----
    - Health check endpoints (/health*) are not logged to reduce noise
    - Requests taking >1 second trigger a WARNING log entry
    - In development, full request headers are logged at DEBUG level
    - In production, only method and path are logged for performance
    """
    start_time = time.time()

    # Skip health check logging to reduce noise
    if request.url.path in ["/health", "/health/ready", "/health/live"]:
        return await call_next(request)

    # Log minimal request info in production
    if settings.ENVIRONMENT == "production":
        logger.info(f"{request.method} {request.url.path}")
    else:
        # Verbose logging for development
        logger.info(f"Request: {request.method} {request.url.path}")
        logger.debug(f"Headers: {dict(request.headers)}")

    response = await call_next(request)

    process_time = time.time() - start_time

    # Log slow requests
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}s - Status: {response.status_code}"
        )
    elif settings.ENVIRONMENT != "production":
        logger.info(f"Response: {response.status_code} (took {process_time:.2f}s)")

    return response


# Middleware - CORS with configurable origins
allowed_origins = settings.get_allowed_origins_list()
logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

app.add_middleware(RateLimitMiddleware, calls_limit=100, time_window=60)

# Routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(agents.router, prefix="/api", tags=["Agents"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(executions.router, prefix="/api", tags=["Executions"])


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint providing basic API information.

    Returns service name, version, environment, and documentation URL.
    Useful for verifying the API is accessible and getting basic metadata.

    Returns
    -------
    dict
        JSON object containing:
        - service: API name
        - version: Current API version
        - environment: Current deployment environment (development/staging/production)
        - docs: URL to interactive API documentation
    """
    return {
        "service": "Agents & Tasks API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint - returns 200 if service is running.
    Use this for simple uptime monitoring.
    """
    return {
        "status": "healthy",
        "message": "Agents & Tasks API is running",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check - verifies service can handle requests.
    Checks database connectivity.
    Use this for load balancer health checks.
    """
    try:
        # Check database connectivity
        from tortoise import connections
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")

        return {
            "status": "ready",
            "checks": {
                "database": "ok",
                "application": "ok"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        from fastapi import status as http_status
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "checks": {
                    "database": "failed",
                    "error": str(e)
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """
    Liveness check - indicates if the service should be restarted.
    Use this for Kubernetes liveness probes.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
