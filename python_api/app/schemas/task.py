"""
Task Schemas Module
==================

This module defines Pydantic schemas for task-related requests and responses.

Schemas
-------
TaskBase : BaseModel
    Base schema with core task fields (title, description)

TaskCreate : TaskBase
    Task creation request with required agent assignments

TaskUpdate : BaseModel
    Task update request (all fields optional for partial updates)

AgentBasic : BaseModel
    Simplified agent schema for task responses

TaskResponse : TaskBase
    Task details response including assigned agents

Schema Features
--------------
TaskCreate enforces business rules:
- At least one agent must be assigned (min_items=1)
- Agent IDs must be valid integers
- All agent IDs must exist in database (validated by service)

TaskResponse includes nested AgentBasic:
- Shows which agents are assigned to the task
- Provides basic agent info without full details
- Enables efficient querying with prefetch_related

Task-Agent Relationship
----------------------
Tasks have many-to-many relationship with agents:
- supported_agent_ids: List of agent IDs (create/update)
- agents: List of AgentBasic objects (response)

Usage in API
-----------
POST /api/tasks (request: TaskCreate, response: TaskResponse):
    Create task with agent assignments

GET /api/tasks (response: List[TaskResponse]):
    List all tasks with their assigned agents

PUT /api/tasks/{id} (request: TaskUpdate, response: TaskResponse):
    Update task and/or reassign agents

Validation
----------
Pydantic validates:
- Required fields present (TaskCreate)
- At least one agent ID provided (min_items=1)
- Field types match expectations
- Agent IDs are valid integers
- Datetime fields are valid ISO 8601

Business logic validation (in service layer):
- All agent IDs exist and are active
- Status values are valid

Examples
--------
Create task:
    POST /api/tasks
    {
        "title": "Process Monthly Reports",
        "description": "Generate and distribute monthly financial reports",
        "supported_agent_ids": [1, 2, 3]
    }

Update task status:
    PUT /api/tasks/1
    {
        "status": "completed"
    }

Update task agents:
    PUT /api/tasks/1
    {
        "supported_agent_ids": [2, 4]
    }

Response:
    {
        "id": 1,
        "title": "Process Monthly Reports",
        "description": "Generate and distribute monthly financial reports",
        "status": "completed",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-20T15:30:00Z",
        "agents": [
            {
                "id": 2,
                "name": "Report Generator",
                "description": "Generates formatted reports"
            },
            {
                "id": 4,
                "name": "Email Sender",
                "description": "Sends emails to recipients"
            }
        ]
    }
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class TaskBase(BaseModel):
    """
    Base schema with core task fields.

    Contains fields common to creation and response schemas.

    Attributes
    ----------
    title : str
        Task title/name (e.g., "Process Payments", "Send Reports")
    description : str
        Detailed task description, requirements, and expected outcomes
    """
    title: str
    description: str


class TaskCreate(TaskBase):
    """
    Task creation request schema.

    Requires task details and at least one agent assignment.

    Attributes
    ----------
    title : str
        Task title (from TaskBase)
    description : str
        Task description (from TaskBase)
    supported_agent_ids : List[int]
        List of agent IDs that can execute this task
        Minimum 1 agent required (validated by Field constraint)

    Examples
    --------
    {
        "title": "Data Backup",
        "description": "Backup database to cloud storage",
        "supported_agent_ids": [1, 3]
    }

    Notes
    -----
    - At least one agent must be assigned
    - All agent IDs must exist and be active (validated by service)
    - Agents can be reassigned later via PUT /api/tasks/{id}
    """
    supported_agent_ids: List[int] = Field(..., min_items=1, description="List of agent IDs that can run this task")


class TaskUpdate(BaseModel):
    """
    Task update request schema for partial updates.

    All fields are optional. Omitted fields will not be modified.

    Attributes
    ----------
    title : str, optional
        New task title
    description : str, optional
        New task description
    supported_agent_ids : List[int], optional
        New list of agent IDs (replaces current assignments)
    status : str, optional
        New task status ('pending', 'running', 'completed', 'failed')

    Examples
    --------
    Update only status:
        {"status": "completed"}

    Update only title:
        {"title": "Updated Task Title"}

    Reassign agents:
        {"supported_agent_ids": [2, 4, 5]}

    Update multiple fields:
        {
            "title": "Enhanced Data Backup",
            "status": "pending",
            "supported_agent_ids": [1, 2]
        }

    Notes
    -----
    - Updating supported_agent_ids replaces all existing assignments
    - All new agent IDs must exist and be active
    - Status should be one of: pending, running, completed, failed
    """
    title: Optional[str] = None
    description: Optional[str] = None
    supported_agent_ids: Optional[List[int]] = None
    status: Optional[str] = None


class AgentBasic(BaseModel):
    """
    Simplified agent schema for task responses.

    Provides basic agent information without timestamps or full details.
    Used in TaskResponse to show which agents are assigned to a task.

    Attributes
    ----------
    id : int
        Agent's unique identifier
    name : str
        Agent's name
    description : str
        Agent's description

    Examples
    --------
    {
        "id": 1,
        "name": "Data Processor",
        "description": "Processes and validates data"
    }

    Notes
    -----
    This is a simplified version of AgentResponse, excluding timestamps
    to keep task responses concise while still providing useful agent info.
    """
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    """
    Task details response schema with assigned agents.

    Returned by GET and POST endpoints. Includes all task fields,
    generated fields, and list of assigned agents.

    Attributes
    ----------
    id : int
        Unique task identifier (auto-generated)
    title : str
        Task title (from TaskBase)
    description : str
        Task description (from TaskBase)
    status : str
        Current task status (pending/running/completed/failed)
    created_at : datetime
        When the task was created (auto-generated)
    updated_at : datetime
        When the task was last modified (auto-updated)
    agents : List[AgentBasic]
        List of agents assigned to this task
        Empty list if no agents assigned (shouldn't happen due to min_items=1)

    Examples
    --------
    {
        "id": 1,
        "title": "Process Invoices",
        "description": "Process pending invoices and send notifications",
        "status": "pending",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
        "agents": [
            {
                "id": 1,
                "name": "Invoice Processor",
                "description": "Processes financial invoices"
            },
            {
                "id": 3,
                "name": "Email Notifier",
                "description": "Sends email notifications"
            }
        ]
    }

    Notes
    -----
    - Uses from_attributes=True to convert from Tortoise ORM models
    - Agents are loaded using prefetch_related for efficiency
    - deleted_at timestamp is not exposed
    - Timestamps are in ISO 8601 format (UTC)
    """
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    agents: List[AgentBasic] = []

    class Config:
        from_attributes = True
