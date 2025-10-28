"""
Agent Schemas Module
===================

This module defines Pydantic schemas for agent-related requests and responses.

Schemas
-------
AgentBase : BaseModel
    Base schema with common agent fields (name, description)

AgentCreate : AgentBase
    Agent creation request (inherits all AgentBase fields)

AgentUpdate : BaseModel
    Agent update request (all fields optional for partial updates)

AgentResponse : AgentBase
    Agent details response (includes id and timestamps)

Schema Inheritance
-----------------
AgentBase defines core agent fields that are:
- Required in AgentCreate (creation request)
- Included in AgentResponse (response)
- Optional in AgentUpdate (update request)

This pattern reduces duplication and ensures consistency.

Usage in API
-----------
POST /api/agents (request: AgentCreate, response: AgentResponse):
    Create a new agent with name and description

GET /api/agents (response: List[AgentResponse]):
    List all agents with full details

GET /api/agents/{id} (response: AgentResponse):
    Get specific agent details

PUT /api/agents/{id} (request: AgentUpdate, response: AgentResponse):
    Update agent (partial updates supported)

Validation
----------
Pydantic automatically validates:
- Required fields are present (AgentCreate)
- Field types match (str for name/description)
- Datetime fields are valid ISO 8601 strings
- No extra fields are provided (default behavior)

Examples
--------
Create agent:
    POST /api/agents
    {
        "name": "Data Analyzer",
        "description": "Analyzes data and generates insights"
    }

Update agent (partial):
    PUT /api/agents/1
    {
        "description": "Enhanced data analysis with ML capabilities"
    }

Response:
    {
        "id": 1,
        "name": "Data Analyzer",
        "description": "Enhanced data analysis with ML capabilities",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-16T14:20:00Z"
    }
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AgentBase(BaseModel):
    """
    Base schema with core agent fields.

    Contains fields common to both creation and response schemas.

    Attributes
    ----------
    name : str
        Agent name (e.g., "Data Processor", "Email Handler")
    description : str
        Detailed description of agent capabilities and purpose
    """
    name: str
    description: str


class AgentCreate(AgentBase):
    """
    Agent creation request schema.

    Inherits all fields from AgentBase (name, description).
    All fields are required for creation.

    Examples
    --------
    {
        "name": "Report Generator",
        "description": "Generates formatted reports from data sources"
    }
    """
    pass


class AgentUpdate(BaseModel):
    """
    Agent update request schema for partial updates.

    All fields are optional, allowing clients to update only specific fields.
    Unset fields will not be modified in the database.

    Attributes
    ----------
    name : str, optional
        New agent name (omit to keep current name)
    description : str, optional
        New description (omit to keep current description)

    Examples
    --------
    Update only name:
        {"name": "Advanced Data Processor"}

    Update only description:
        {"description": "Now supports real-time processing"}

    Update both:
        {
            "name": "ML Data Processor",
            "description": "Machine learning powered data processing"
        }
    """
    name: Optional[str] = None
    description: Optional[str] = None


class AgentResponse(AgentBase):
    """
    Agent details response schema.

    Returned by GET and POST endpoints. Includes all agent fields
    plus generated fields (id, timestamps).

    Attributes
    ----------
    id : int
        Unique agent identifier (auto-generated)
    name : str
        Agent name (from AgentBase)
    description : str
        Agent description (from AgentBase)
    created_at : datetime
        When the agent was created (auto-generated)
    updated_at : datetime
        When the agent was last modified (auto-updated)

    Examples
    --------
    {
        "id": 1,
        "name": "Data Analyzer",
        "description": "Analyzes data patterns and trends",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }

    Notes
    -----
    - Uses from_attributes=True to convert from Tortoise ORM models
    - deleted_at timestamp is not exposed in responses
    - Timestamps are in ISO 8601 format (UTC)
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
