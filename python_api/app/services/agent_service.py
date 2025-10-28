"""
Agent Service Module
===================

This module provides business logic for agent management operations.

The AgentService class handles:
- CRUD operations for agents
- Agent validation and existence checks
- Soft delete implementation
- Error handling with appropriate HTTP exceptions

Service Layer Pattern
--------------------
This service sits between the router layer (HTTP) and the model layer (database):
- Routers: Handle HTTP requests/responses
- Services: Implement business logic and validation
- Models: Define database structure and queries

This separation provides:
- Reusable business logic across multiple endpoints
- Centralized validation and error handling
- Easier testing (can test business logic without HTTP)
- Clean architecture with clear responsibilities

Soft Delete
----------
Agent deletions are "soft" - the deleted_at timestamp is set instead of
removing the record. This provides:
- Data retention for audit purposes
- Referential integrity with related records
- Ability to recover deleted agents if needed

All query methods filter out soft-deleted agents automatically.

Error Handling
-------------
All methods raise HTTPException with appropriate status codes:
- 404 NOT FOUND: Agent doesn't exist or is soft-deleted
- 400 BAD REQUEST: Invalid input or business rule violation

Usage
-----
In routers:
    from app.services.agent_service import AgentService
    from app.schemas.agent import AgentCreate

    # Create agent
    agent_data = AgentCreate(name="Processor", description="Processes data")
    agent = await AgentService.create_agent(agent_data)

    # Get agent
    agent = await AgentService.get_agent_by_id(1)

    # Verify agents exist
    exists = await AgentService.verify_agents_exist([1, 2, 3])

Dependencies
-----------
- Tortoise ORM: Database operations
- FastAPI HTTPException: Error handling
- Pydantic schemas: Request validation
"""

from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    """
    Service class providing agent management business logic.

    Implements CRUD operations and validation for Agent resources.
    All methods are static as they don't require instance state.

    Methods
    -------
    get_all_agents()
        Retrieve all active (non-deleted) agents

    get_agent_by_id(agent_id)
        Retrieve specific agent by ID, raises 404 if not found

    create_agent(agent_data)
        Create new agent from validated schema

    update_agent(agent_id, agent_data)
        Update existing agent with partial data

    delete_agent(agent_id)
        Soft delete agent (set deleted_at timestamp)

    verify_agents_exist(agent_ids)
        Check if all provided agent IDs exist and are active
    """
    @staticmethod
    async def get_all_agents() -> List[Agent]:
        """
        Retrieve all active (non-deleted) agents.

        Returns
        -------
        List[Agent]
            List of all active Agent instances, empty list if none exist

        Examples
        --------
        agents = await AgentService.get_all_agents()
        for agent in agents:
            print(f"{agent.name}: {agent.description}")
        """
        return await Agent.filter(deleted_at__isnull=True).all()

    @staticmethod
    async def get_agent_by_id(agent_id: int) -> Agent:
        """
        Retrieve a specific agent by ID.

        Only returns active (non-deleted) agents.

        Parameters
        ----------
        agent_id : int
            Unique identifier of the agent

        Returns
        -------
        Agent
            The requested Agent instance

        Raises
        ------
        HTTPException (404 NOT FOUND)
            If agent doesn't exist or is soft-deleted

        Examples
        --------
        try:
            agent = await AgentService.get_agent_by_id(1)
            print(f"Found: {agent.name}")
        except HTTPException as e:
            print(f"Agent not found: {e.detail}")
        """
        agent = await Agent.filter(id=agent_id, deleted_at__isnull=True).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with id {agent_id} not found"
            )
        return agent

    @staticmethod
    async def create_agent(agent_data: AgentCreate) -> Agent:
        """
        Create a new agent from validated data.

        Parameters
        ----------
        agent_data : AgentCreate
            Validated agent creation schema with name and description

        Returns
        -------
        Agent
            Newly created Agent instance with generated ID and timestamps

        Examples
        --------
        from app.schemas.agent import AgentCreate

        agent_data = AgentCreate(
            name="Data Processor",
            description="Processes incoming data streams"
        )
        agent = await AgentService.create_agent(agent_data)
        print(f"Created agent with ID: {agent.id}")
        """
        agent = await Agent.create(
            name=agent_data.name,
            description=agent_data.description
        )
        return agent

    @staticmethod
    async def update_agent(agent_id: int, agent_data: AgentUpdate) -> Agent:
        """
        Update an existing agent with partial data.

        Only fields present in agent_data are updated. Omitted fields
        retain their current values.

        Parameters
        ----------
        agent_id : int
            ID of the agent to update
        agent_data : AgentUpdate
            Validated update schema with optional name/description

        Returns
        -------
        Agent
            Updated Agent instance

        Raises
        ------
        HTTPException (404 NOT FOUND)
            If agent doesn't exist or is soft-deleted

        Examples
        --------
        from app.schemas.agent import AgentUpdate

        # Update only description
        update_data = AgentUpdate(description="Enhanced capabilities")
        agent = await AgentService.update_agent(1, update_data)

        # Update both fields
        update_data = AgentUpdate(
            name="Advanced Processor",
            description="ML-powered data processing"
        )
        agent = await AgentService.update_agent(1, update_data)
        """
        agent = await AgentService.get_agent_by_id(agent_id)

        update_data = agent_data.model_dump(exclude_unset=True)
        if update_data:
            await agent.update_from_dict(update_data).save()

        return agent

    @staticmethod
    async def delete_agent(agent_id: int) -> None:
        """
        Soft delete an agent by setting deleted_at timestamp.

        The agent record remains in the database but is excluded from
        queries. This preserves audit trail and referential integrity.

        Parameters
        ----------
        agent_id : int
            ID of the agent to delete

        Raises
        ------
        HTTPException (404 NOT FOUND)
            If agent doesn't exist or is already deleted

        Examples
        --------
        await AgentService.delete_agent(1)
        # Agent is soft-deleted, not physically removed

        # Subsequent get will raise 404
        try:
            agent = await AgentService.get_agent_by_id(1)
        except HTTPException:
            print("Agent is deleted")
        """
        agent = await AgentService.get_agent_by_id(agent_id)
        agent.deleted_at = datetime.utcnow()
        await agent.save()

    @staticmethod
    async def verify_agents_exist(agent_ids: List[int]) -> bool:
        """
        Verify that all provided agent IDs exist and are active.

        Used for validating agent assignments before creating/updating tasks.

        Parameters
        ----------
        agent_ids : List[int]
            List of agent IDs to verify

        Returns
        -------
        bool
            True if all agent IDs exist and are active, False otherwise

        Examples
        --------
        # Verify before creating task
        agent_ids = [1, 2, 3]
        if await AgentService.verify_agents_exist(agent_ids):
            # All agents exist, proceed with task creation
            task = await TaskService.create_task(task_data)
        else:
            # One or more agents don't exist
            raise HTTPException(400, "Invalid agent IDs")

        Notes
        -----
        Returns False if:
        - Any agent ID doesn't exist in database
        - Any agent is soft-deleted
        - Empty list is provided (count=0, len=0, returns True)
        """
        count = await Agent.filter(id__in=agent_ids, deleted_at__isnull=True).count()
        return count == len(agent_ids)
