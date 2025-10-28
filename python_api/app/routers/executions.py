"""
Executions Router Module
========================

This module provides RESTful endpoints for managing task executions.

Endpoints
--------
POST /api/executions
    Start execution of a task by a specific agent

GET /api/executions
    Get list of all executions (all statuses)

GET /api/executions/running
    Get list of currently running executions only

GET /api/executions/{execution_id}
    Get specific execution details by ID

Execution Lifecycle
------------------
1. Create execution (POST /api/executions)
   - Status: 'running'
   - started_at: Current timestamp
   - completed_at: null

2. Execution completes successfully
   - Status: 'completed'
   - completed_at: Set to current timestamp
   - result: Execution output/result data

3. Execution fails
   - Status: 'failed'
   - completed_at: Set to current timestamp
   - error_message: Error details

Execution Status Values
----------------------
- 'running': Execution is currently in progress
- 'completed': Execution finished successfully
- 'failed': Execution failed with an error

Task-Agent Authorization
-----------------------
When creating an execution:
- The specified agent must be assigned to the specified task
- If agent is not authorized for the task, returns 400 Bad Request
- Agent-task assignments are managed via the tasks endpoints

Authentication
-------------
All endpoints require JWT authentication. Include token in Authorization header:
    Authorization: Bearer <access_token>

Request/Response Models
----------------------
ExecutionCreate (request):
    - task_id: int (required)
    - agent_id: int (required)

ExecutionResponse (response):
    - id: int
    - task_id: int
    - agent_id: int
    - status: str ('running', 'completed', 'failed')
    - started_at: datetime
    - completed_at: datetime | None
    - result: str | None (execution output)
    - error_message: str | None (error details if failed)

Read-Only Operations
-------------------
Note: This router only provides read and create operations.
Update and delete operations are typically handled by:
- Background workers that update execution status
- Cascade deletion when parent tasks/agents are deleted

Error Responses
--------------
200 OK: Successful GET operations
201 Created: Successful POST operations
400 Bad Request: Agent not authorized for task
401 Unauthorized: Missing or invalid JWT token
404 Not Found: Execution, task, or agent not found
422 Unprocessable Entity: Invalid request body

Usage Examples
-------------
Start a task execution:
    POST /api/executions
    {
        "task_id": 1,
        "agent_id": 2
    }

List all executions:
    GET /api/executions

List only running executions:
    GET /api/executions/running

Get specific execution:
    GET /api/executions/1

Monitoring Executions
--------------------
To monitor execution progress:
1. Create execution via POST /api/executions
2. Poll GET /api/executions/{id} to check status
3. When status changes from 'running' to 'completed' or 'failed',
   check result or error_message fields

For real-world applications, consider implementing:
- WebSocket connections for real-time updates
- Webhook callbacks when execution completes
- Background job queues (Celery, RQ) for actual task execution
"""

from typing import List
from fastapi import APIRouter, Depends, status, Security

from app.schemas.execution import ExecutionCreate, ExecutionResponse
from app.services.execution_service import ExecutionService
from app.dependencies import get_current_user, security
from app.models.user import User

router = APIRouter(dependencies=[Security(security)])


@router.post(
    "/executions",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start task execution"
)
async def create_execution(execution_data: ExecutionCreate, current_user: User = Depends(get_current_user)):
    """
    Start executing a task with a specific agent.

    **Request Body:**
    - task_id: ID of the task to execute
    - agent_id: ID of the agent to run the task

    **Returns:**
    - Execution details with status 'running'

    **Errors:**
    - 404: Task or agent not found
    - 400: Agent is not authorized to run the specified task

    **Authentication:**
    - Requires valid JWT token
    """
    execution = await ExecutionService.create_execution(execution_data)
    return execution


@router.get(
    "/executions",
    response_model=List[ExecutionResponse],
    summary="Get all executions"
)
async def get_executions(current_user: User = Depends(get_current_user)):
    """
    Get a list of all task executions.

    **Returns:**
    - List of all executions with their status

    **Authentication:**
    - Requires valid JWT token
    """
    executions = await ExecutionService.get_all_executions()
    return executions


@router.get(
    "/executions/running",
    response_model=List[ExecutionResponse],
    summary="Get running executions"
)
async def get_running_executions(current_user: User = Depends(get_current_user)):
    """
    Get a list of currently running task executions.

    **Returns:**
    - List of executions with status 'running'

    **Authentication:**
    - Requires valid JWT token
    """
    executions = await ExecutionService.get_running_executions()
    return executions


@router.get(
    "/executions/{execution_id}",
    response_model=ExecutionResponse,
    summary="Get execution by ID"
)
async def get_execution(execution_id: int, current_user: User = Depends(get_current_user)):
    """
    Get a specific execution by ID.

    **Parameters:**
    - execution_id: ID of the execution

    **Returns:**
    - Execution details

    **Errors:**
    - 404: Execution not found

    **Authentication:**
    - Requires valid JWT token
    """
    execution = await ExecutionService.get_execution_by_id(execution_id)
    return execution
