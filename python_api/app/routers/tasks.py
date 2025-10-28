"""
Tasks Router Module
==================

This module provides RESTful endpoints for managing tasks and their agent assignments.

Endpoints
--------
GET /api/tasks
    Get list of all active tasks with their assigned agents

POST /api/tasks
    Create a new task and assign it to one or more agents

GET /api/tasks/{task_id}
    Get specific task details including assigned agents

PUT /api/tasks/{task_id}
    Update task details and/or reassign agents

DELETE /api/tasks/{task_id}
    Soft delete a task (sets deleted_at timestamp)

CRUD Operations
--------------
All endpoints implement standard REST CRUD operations:
- Create: POST /api/tasks (201 Created on success)
- Read: GET /api/tasks (list) or GET /api/tasks/{id} (single)
- Update: PUT /api/tasks/{id} (partial updates supported)
- Delete: DELETE /api/tasks/{id} (soft delete, 204 No Content)

Task-Agent Relationship
----------------------
Tasks have a many-to-many relationship with agents:
- Each task can be assigned to multiple agents
- Each agent can be assigned to multiple tasks
- At least one agent must be assigned when creating a task
- Agent assignments can be updated via PUT endpoint

Task Status
----------
Tasks have a status field with these values:
- 'pending': Task created but not yet executed
- 'running': Task is currently being executed
- 'completed': Task execution finished successfully
- 'failed': Task execution failed

Authentication
-------------
All endpoints require JWT authentication. Include token in Authorization header:
    Authorization: Bearer <access_token>

Request/Response Models
----------------------
TaskCreate (request):
    - title: str (required)
    - description: str (required)
    - supported_agent_ids: List[int] (required, min 1 agent)

TaskUpdate (request):
    - title: str (optional)
    - description: str (optional)
    - supported_agent_ids: List[int] (optional)
    - status: str (optional)

TaskResponse (response):
    - id: int
    - title: str
    - description: str
    - status: str
    - created_at: datetime
    - updated_at: datetime
    - agents: List[AgentBasic] (assigned agents with id, name, description)

Agent Validation
---------------
When creating or updating tasks with agent assignments:
- All agent IDs must exist in the database
- All agents must be active (not soft-deleted)
- If any agent ID is invalid, returns 400 Bad Request

Error Responses
--------------
200 OK: Successful GET/PUT operations
201 Created: Successful POST operations
204 No Content: Successful DELETE operations
400 Bad Request: Invalid agent IDs provided
401 Unauthorized: Missing or invalid JWT token
404 Not Found: Task with specified ID doesn't exist or is deleted
422 Unprocessable Entity: Invalid request body

Usage Examples
-------------
Create a task:
    POST /api/tasks
    {
        "title": "Process Monthly Reports",
        "description": "Generate and send monthly financial reports",
        "supported_agent_ids": [1, 2, 3]
    }

Update task status:
    PUT /api/tasks/1
    {
        "status": "completed"
    }

Reassign agents:
    PUT /api/tasks/1
    {
        "supported_agent_ids": [2, 4]
    }

List all tasks:
    GET /api/tasks

Get specific task with agents:
    GET /api/tasks/1

Delete a task:
    DELETE /api/tasks/1
"""

from typing import List
from fastapi import APIRouter, Depends, status, Security

from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService
from app.dependencies import get_current_user, security
from app.models.user import User

router = APIRouter(dependencies=[Security(security)])


@router.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="Get all tasks"
)
async def get_tasks(current_user: User = Depends(get_current_user)):
    """
    Get a list of all tasks with their supported agents.

    **Returns:**
    - List of tasks with id, title, description, status, and supported agents

    **Authentication:**
    - Requires valid JWT token
    """
    tasks = await TaskService.get_all_tasks()
    return tasks


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task"
)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    """
    Create a new task with one or more supported agents.

    **Request Body:**
    - title: Task title
    - description: Task description
    - supported_agent_ids: List of agent IDs that can run this task (at least one required)

    **Returns:**
    - Created task with unique id and associated agents

    **Errors:**
    - 400: One or more agent IDs do not exist

    **Authentication:**
    - Requires valid JWT token
    """
    task = await TaskService.create_task(task_data)
    return task


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID"
)
async def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    """
    Get a specific task by ID with its supported agents.

    **Parameters:**
    - task_id: ID of the task

    **Returns:**
    - Task details with supported agents

    **Errors:**
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token
    """
    task = await TaskService.get_task_by_id(task_id)
    return task


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update task"
)
async def update_task(task_id: int, task_data: TaskUpdate, current_user: User = Depends(get_current_user)):
    """
    Update an existing task.

    **Parameters:**
    - task_id: ID of the task to update

    **Request Body:**
    - title: New task title (optional)
    - description: New task description (optional)
    - supported_agent_ids: New list of agent IDs (optional)
    - status: New task status (optional)

    **Returns:**
    - Updated task

    **Errors:**
    - 404: Task not found
    - 400: One or more agent IDs do not exist

    **Authentication:**
    - Requires valid JWT token
    """
    task = await TaskService.update_task(task_id, task_data)
    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task"
)
async def delete_task(task_id: int, current_user: User = Depends(get_current_user)):
    """
    Soft delete a task.

    **Parameters:**
    - task_id: ID of the task to delete

    **Returns:**
    - 204 No Content on success

    **Errors:**
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token
    """
    await TaskService.delete_task(task_id)
    return None
