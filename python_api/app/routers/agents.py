"""
Agents Router Module
===================

This module provides RESTful endpoints for managing AI agents.

Endpoints
--------
GET /api/agents
    Get list of all active (non-deleted) agents

POST /api/agents
    Create a new agent with name and description

GET /api/agents/{agent_id}
    Get specific agent details by ID

PUT /api/agents/{agent_id}
    Update existing agent (name and/or description)

DELETE /api/agents/{agent_id}
    Soft delete an agent (sets deleted_at timestamp)

CRUD Operations
--------------
All endpoints implement standard REST CRUD operations:
- Create: POST /api/agents (201 Created on success)
- Read: GET /api/agents (list) or GET /api/agents/{id} (single)
- Update: PUT /api/agents/{id} (partial updates supported)
- Delete: DELETE /api/agents/{id} (soft delete, 204 No Content)

Authentication
-------------
All endpoints require JWT authentication. Include token in Authorization header:
    Authorization: Bearer <access_token>

The router uses Security(security) at the router level, meaning all routes
inherit authentication requirements. Individual routes also use
Depends(get_current_user) to access the authenticated user object.

Request/Response Models
----------------------
AgentCreate (request):
    - name: str (required)
    - description: str (required)

AgentUpdate (request):
    - name: str (optional)
    - description: str (optional)

AgentResponse (response):
    - id: int
    - name: str
    - description: str
    - created_at: datetime
    - updated_at: datetime

Soft Delete
----------
DELETE operations don't remove agents from the database. Instead, they set
the deleted_at timestamp. This allows:
- Data retention for audit purposes
- Referential integrity with related records
- Potential for recovery/undelete functionality

Error Responses
--------------
200 OK: Successful GET/PUT operations
201 Created: Successful POST operations
204 No Content: Successful DELETE operations
401 Unauthorized: Missing or invalid JWT token
404 Not Found: Agent with specified ID doesn't exist or is deleted
422 Unprocessable Entity: Invalid request body

Usage Examples
-------------
Create an agent:
    POST /api/agents
    {
        "name": "Data Processor",
        "description": "Processes and analyzes data streams"
    }

Update an agent (partial):
    PUT /api/agents/1
    {
        "description": "Enhanced data processing capabilities"
    }

List all agents:
    GET /api/agents

Get specific agent:
    GET /api/agents/1

Delete an agent:
    DELETE /api/agents/1
"""

from typing import List
from fastapi import APIRouter, Depends, status, Security

from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from app.services.agent_service import AgentService
from app.dependencies import get_current_user, security
from app.models.user import User

router = APIRouter(dependencies=[Security(security)])


@router.get(
    "/agents",
    response_model=List[AgentResponse],
    summary="Get all agents"
)
async def get_agents(current_user: User = Depends(get_current_user)):
    """
    Get a list of all agents.

    **Returns:**
    - List of agents with id, name, description, and timestamps

    **Authentication:**
    - Requires valid JWT token
    """
    agents = await AgentService.get_all_agents()
    return agents


@router.post(
    "/agents",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new agent"
)
async def create_agent(agent_data: AgentCreate, current_user: User = Depends(get_current_user)):
    """
    Create a new agent.

    **Request Body:**
    - name: Agent name
    - description: Agent description

    **Returns:**
    - Created agent with unique id

    **Authentication:**
    - Requires valid JWT token
    """
    agent = await AgentService.create_agent(agent_data)
    return agent


@router.get(
    "/agents/{agent_id}",
    response_model=AgentResponse,
    summary="Get agent by ID"
)
async def get_agent(agent_id: int, current_user: User = Depends(get_current_user)):
    """
    Get a specific agent by ID.

    **Parameters:**
    - agent_id: ID of the agent

    **Returns:**
    - Agent details

    **Errors:**
    - 404: Agent not found

    **Authentication:**
    - Requires valid JWT token
    """
    agent = await AgentService.get_agent_by_id(agent_id)
    return agent


@router.put(
    "/agents/{agent_id}",
    response_model=AgentResponse,
    summary="Update agent"
)
async def update_agent(agent_id: int, agent_data: AgentUpdate, current_user: User = Depends(get_current_user)):
    """
    Update an existing agent.

    **Parameters:**
    - agent_id: ID of the agent to update

    **Request Body:**
    - name: New agent name (optional)
    - description: New agent description (optional)

    **Returns:**
    - Updated agent

    **Errors:**
    - 404: Agent not found

    **Authentication:**
    - Requires valid JWT token
    """
    agent = await AgentService.update_agent(agent_id, agent_data)
    return agent


@router.delete(
    "/agents/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete agent"
)
async def delete_agent(agent_id: int, current_user: User = Depends(get_current_user)):
    """
    Soft delete an agent.

    **Parameters:**
    - agent_id: ID of the agent to delete

    **Returns:**
    - 204 No Content on success

    **Errors:**
    - 404: Agent not found

    **Authentication:**
    - Requires valid JWT token
    """
    await AgentService.delete_agent(agent_id)
    return None
