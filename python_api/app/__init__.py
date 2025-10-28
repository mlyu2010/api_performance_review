"""
Agents & Tasks API - Application Package
========================================

This package contains the complete Agents & Tasks REST API application.

Package Structure
----------------
app/
├── __init__.py           # Package initialization (this file)
├── main.py               # FastAPI application and main entry point
├── config.py             # Application configuration and settings
├── dependencies.py       # Dependency injection functions (auth, etc.)
├── models/               # Tortoise ORM database models
│   ├── user.py          # User model with password hashing
│   ├── agent.py         # Agent model
│   ├── task.py          # Task and TaskAgent models
│   └── execution.py     # Execution model
├── routers/              # FastAPI route handlers (endpoints)
│   ├── auth.py          # Authentication endpoints (login, register)
│   ├── agents.py        # Agent CRUD endpoints
│   ├── tasks.py         # Task CRUD endpoints
│   └── executions.py    # Execution CRUD endpoints
├── schemas/              # Pydantic models for request/response validation
│   ├── auth.py          # Login, token schemas
│   ├── agent.py         # Agent create/update schemas
│   ├── task.py          # Task create/update schemas
│   └── execution.py     # Execution schemas
├── services/             # Business logic layer
│   ├── auth_service.py  # JWT token generation and validation
│   ├── agent_service.py # Agent business logic
│   ├── task_service.py  # Task business logic
│   └── execution_service.py # Execution business logic
└── middleware/           # Custom middleware
    └── rate_limiter.py  # Rate limiting middleware

Usage
-----
Import the FastAPI application instance:
    from app import app

Run with uvicorn:
    uvicorn app:app --reload --host 0.0.0.0 --port 8000

Or with gunicorn for production:
    gunicorn app:app -c gunicorn_conf.py

Exported Symbols
---------------
app : FastAPI
    The main FastAPI application instance
"""

from app.main import app

__all__ = ["app"]
