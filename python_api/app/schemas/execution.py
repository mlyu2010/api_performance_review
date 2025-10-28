"""
Execution Schemas Module
========================

This module defines Pydantic schemas for execution-related requests and responses.

Schemas
-------
ExecutionCreate : BaseModel
    Execution start request (task_id + agent_id)

ExecutionResponse : BaseModel
    Execution details response with status and timing

Execution Lifecycle
------------------
1. Create (ExecutionCreate):
   - Client specifies task_id and agent_id
   - Server validates agent is authorized for task
   - Execution starts with status='running'

2. Monitor (ExecutionResponse):
   - Poll GET /api/executions/{id} to check status
   - Status changes to 'completed' or 'failed' when done
   - Result or error_message is populated

3. Complete:
   - Status: 'completed', result contains output
   - Status: 'failed', error_message contains error details

Authorization
------------
When creating an execution:
- Agent must be assigned to the task
- If not assigned, returns 400 Bad Request
- Assignment is managed via task endpoints

Status Values
------------
- 'running': Execution in progress
- 'completed': Execution finished successfully
- 'failed': Execution failed with error

Usage in API
-----------
POST /api/executions (request: ExecutionCreate, response: ExecutionResponse):
    Start task execution by specific agent

GET /api/executions/{id} (response: ExecutionResponse):
    Get execution details and status

GET /api/executions (response: List[ExecutionResponse]):
    List all executions

GET /api/executions/running (response: List[ExecutionResponse]):
    List only running executions

Validation
----------
Pydantic validates:
- task_id and agent_id are valid integers
- Datetime fields are valid ISO 8601
- Optional fields can be null

Service layer validates:
- Task and agent exist and are active
- Agent is authorized to execute the task

Examples
--------
Start execution:
    POST /api/executions
    {
        "task_id": 1,
        "agent_id": 2
    }

Running execution response:
    {
        "id": 1,
        "task_id": 1,
        "agent_id": 2,
        "status": "running",
        "started_at": "2024-01-15T10:00:00Z",
        "completed_at": null,
        "result": null,
        "error_message": null
    }

Completed execution response:
    {
        "id": 1,
        "task_id": 1,
        "agent_id": 2,
        "status": "completed",
        "started_at": "2024-01-15T10:00:00Z",
        "completed_at": "2024-01-15T10:05:30Z",
        "result": "Processed 150 records successfully",
        "error_message": null
    }

Failed execution response:
    {
        "id": 2,
        "task_id": 3,
        "agent_id": 5,
        "status": "failed",
        "started_at": "2024-01-15T11:00:00Z",
        "completed_at": "2024-01-15T11:02:15Z",
        "result": null,
        "error_message": "Database connection timeout after 30 seconds"
    }
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ExecutionCreate(BaseModel):
    """
    Execution start request schema.

    Specifies which task should be executed by which agent.

    Attributes
    ----------
    task_id : int
        ID of the task to execute (must exist and be active)
    agent_id : int
        ID of the agent to execute the task (must be assigned to task)

    Examples
    --------
    {
        "task_id": 1,
        "agent_id": 2
    }

    Notes
    -----
    - Both task and agent must exist and be active
    - Agent must be assigned to the task (via task.agents)
    - If agent not authorized, service returns 400 Bad Request
    - Execution immediately starts with status='running'
    """
    task_id: int
    agent_id: int


class ExecutionResponse(BaseModel):
    """
    Execution details response schema.

    Provides complete execution information including status, timing,
    results, and error details.

    Attributes
    ----------
    id : int
        Unique execution identifier (auto-generated)
    task_id : int
        ID of the task being executed
    agent_id : int
        ID of the agent executing the task
    status : str
        Current execution status ('running', 'completed', 'failed')
    started_at : datetime
        When the execution started (auto-populated on creation)
    completed_at : datetime, optional
        When the execution finished (null if still running)
    result : str, optional
        Execution output/result data (null if running or failed)
    error_message : str, optional
        Error details if execution failed (null if running or completed)

    Examples
    --------
    Running execution:
        {
            "id": 1,
            "task_id": 5,
            "agent_id": 3,
            "status": "running",
            "started_at": "2024-01-15T14:30:00Z",
            "completed_at": null,
            "result": null,
            "error_message": null
        }

    Completed execution:
        {
            "id": 1,
            "task_id": 5,
            "agent_id": 3,
            "status": "completed",
            "started_at": "2024-01-15T14:30:00Z",
            "completed_at": "2024-01-15T14:35:20Z",
            "result": "Successfully processed 500 records in 5 minutes",
            "error_message": null
        }

    Failed execution:
        {
            "id": 2,
            "task_id": 7,
            "agent_id": 4,
            "status": "failed",
            "started_at": "2024-01-15T15:00:00Z",
            "completed_at": "2024-01-15T15:00:45Z",
            "result": null,
            "error_message": "API rate limit exceeded: 429 Too Many Requests"
        }

    Notes
    -----
    - Uses from_attributes=True to convert from Tortoise ORM models
    - Timestamps are in ISO 8601 format (UTC)
    - Result and error_message are mutually exclusive (only one should be set)
    - completed_at is null while status is 'running'
    - For monitoring, poll this endpoint until status changes from 'running'
    """
    id: int
    task_id: int
    agent_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
