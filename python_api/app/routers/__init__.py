"""
API Routers Package
==================

This package contains all FastAPI router modules for the Agents & Tasks API.

Router Modules
-------------
auth : APIRouter
    Authentication endpoints (login)
    - POST /api/login: User authentication and JWT token generation

agents : APIRouter
    Agent management endpoints (CRUD operations)
    - GET /api/agents: List all agents
    - POST /api/agents: Create new agent
    - GET /api/agents/{agent_id}: Get agent by ID
    - PUT /api/agents/{agent_id}: Update agent
    - DELETE /api/agents/{agent_id}: Soft delete agent

tasks : APIRouter
    Task management endpoints (CRUD operations)
    - GET /api/tasks: List all tasks with agents
    - POST /api/tasks: Create new task with agent assignments
    - GET /api/tasks/{task_id}: Get task by ID
    - PUT /api/tasks/{task_id}: Update task
    - DELETE /api/tasks/{task_id}: Soft delete task

executions : APIRouter
    Task execution endpoints
    - POST /api/executions: Start task execution
    - GET /api/executions: List all executions
    - GET /api/executions/running: List running executions
    - GET /api/executions/{execution_id}: Get execution by ID

Architecture
-----------
Each router module:
1. Defines FastAPI APIRouter instance
2. Implements route handlers for specific endpoints
3. Uses Pydantic schemas for request/response validation
4. Delegates business logic to service layer
5. Requires JWT authentication (except login endpoint)

Authentication
-------------
All routers except 'auth' require JWT authentication via the
Security(security) dependency or Depends(get_current_user).

Usage in app/main.py
-------------------
    from app.routers import auth, agents, tasks, executions

    app.include_router(auth.router, prefix="/api", tags=["Authentication"])
    app.include_router(agents.router, prefix="/api", tags=["Agents"])
    app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
    app.include_router(executions.router, prefix="/api", tags=["Executions"])

Tags
----
Routers are organized in Swagger UI using tags:
- Authentication: User login and token management
- Agents: AI agent management
- Tasks: Task management and agent assignments
- Executions: Task execution tracking
"""

# Routers package initialization
