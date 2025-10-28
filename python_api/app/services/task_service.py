"""
Task Service Module
==================

This module provides business logic for task management operations.

The TaskService class handles:
- CRUD operations for tasks
- Task-agent relationship management (many-to-many)
- Task validation and business rules
- Soft delete implementation
- Error handling with appropriate HTTP exceptions

Task-Agent Relationship
----------------------
Tasks have a many-to-many relationship with agents:
- Each task can be assigned to multiple agents
- Each agent can be assigned to multiple tasks
- Minimum one agent required per task
- Agents must exist and be active

The service manages this relationship through:
- Agent validation before task creation/update
- Automatic relationship updates via Tortoise ORM
- Prefetching agents for efficient queries

Service Layer Pattern
--------------------
This service sits between routers and models:
- Handles business logic and validation
- Manages complex relationships
- Provides reusable operations
- Centralizes error handling

Soft Delete
----------
Task deletions are "soft" - the deleted_at timestamp is set.
All query methods automatically filter out soft-deleted tasks.

Task Status
----------
Tasks have status field with values:
- 'pending': Created but not yet executed
- 'running': Currently being executed
- 'completed': Execution finished successfully
- 'failed': Execution failed

Usage
-----
In routers:
    from app.services.task_service import TaskService
    from app.schemas.task import TaskCreate

    # Create task with agents
    task_data = TaskCreate(
        title="Process Data",
        description="Process incoming data",
        supported_agent_ids=[1, 2, 3]
    )
    task = await TaskService.create_task(task_data)

    # Get task with agents
    task = await TaskService.get_task_by_id(1)
    print(f"Task has {len(task.agents)} agents")

Dependencies
-----------
- Tortoise ORM: Database operations and relationships
- AgentService: Agent validation
- FastAPI HTTPException: Error handling
- Pydantic schemas: Request validation
"""

from datetime import datetime
from typing import List
from fastapi import HTTPException, status

from app.models.task import Task
from app.models.agent import Agent
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.agent_service import AgentService


class TaskService:
    """
    Service class providing task management business logic.

    Implements CRUD operations, agent relationship management,
    and validation for Task resources.

    Methods
    -------
    get_all_tasks()
        Retrieve all active tasks with their assigned agents

    get_task_by_id(task_id)
        Retrieve specific task by ID with agents, raises 404 if not found

    create_task(task_data)
        Create new task and assign it to agents

    update_task(task_id, task_data)
        Update task details and/or reassign agents

    delete_task(task_id)
        Soft delete task (set deleted_at timestamp)
    """
    @staticmethod
    async def get_all_tasks() -> List[Task]:
        """
        Retrieve all active tasks with their assigned agents.

        Uses prefetch_related for efficient loading of the many-to-many
        agent relationship, avoiding N+1 query problems.

        Returns
        -------
        List[Task]
            List of all active Task instances with agents loaded,
            empty list if no tasks exist

        Examples
        --------
        tasks = await TaskService.get_all_tasks()
        for task in tasks:
            print(f"{task.title}: {len(task.agents)} agents")
            for agent in task.agents:
                print(f"  - {agent.name}")
        """
        tasks = await Task.filter(deleted_at__isnull=True).prefetch_related("agents").all()
        return tasks

    @staticmethod
    async def get_task_by_id(task_id: int) -> Task:
        """
        Retrieve a specific task by ID with its assigned agents.

        Only returns active (non-deleted) tasks. Prefetches agents
        for efficient access to the relationship.

        Parameters
        ----------
        task_id : int
            Unique identifier of the task

        Returns
        -------
        Task
            The requested Task instance with agents loaded

        Raises
        ------
        HTTPException (404 NOT FOUND)
            If task doesn't exist or is soft-deleted

        Examples
        --------
        try:
            task = await TaskService.get_task_by_id(1)
            print(f"Task: {task.title}")
            print(f"Agents: {[a.name for a in task.agents]}")
        except HTTPException as e:
            print(f"Task not found: {e.detail}")
        """
        task = await Task.filter(id=task_id, deleted_at__isnull=True).prefetch_related("agents").first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        return task

    @staticmethod
    async def create_task(task_data: TaskCreate) -> Task:
        """
        Create a new task and assign it to multiple agents.

        Validates that all provided agent IDs exist and are active before
        creating the task. Creates the task first, then establishes the
        many-to-many relationships with agents.

        Parameters
        ----------
        task_data : TaskCreate
            Validated task creation schema with title, description,
            and list of agent IDs (minimum 1 required)

        Returns
        -------
        Task
            Newly created Task instance with agents loaded

        Raises
        ------
        HTTPException (400 BAD REQUEST)
            If any agent ID doesn't exist or is soft-deleted

        Examples
        --------
        from app.schemas.task import TaskCreate

        task_data = TaskCreate(
            title="Process Reports",
            description="Generate monthly reports",
            supported_agent_ids=[1, 2, 3]
        )
        task = await TaskService.create_task(task_data)
        print(f"Created task {task.id} with {len(task.agents)} agents")

        Notes
        -----
        Transaction flow:
        1. Validate all agent IDs exist
        2. Create task record
        3. Create TaskAgent junction records
        4. Fetch task with agents for response
        """
        # Verify all agents exist
        if not await AgentService.verify_agents_exist(task_data.supported_agent_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more agent IDs do not exist"
            )

        # Create task
        task = await Task.create(
            title=task_data.title,
            description=task_data.description
        )

        # Add agents to task
        agents = await Agent.filter(id__in=task_data.supported_agent_ids)
        await task.agents.add(*agents)

        # Fetch with agents for response
        await task.fetch_related("agents")
        return task

    @staticmethod
    async def update_task(task_id: int, task_data: TaskUpdate) -> Task:
        """
        Update an existing task with partial data.

        Supports updating:
        - Task fields (title, description, status)
        - Agent assignments (replaces all existing assignments)

        Only fields present in task_data are updated. Omitted fields
        retain their current values.

        Parameters
        ----------
        task_id : int
            ID of the task to update
        task_data : TaskUpdate
            Validated update schema with optional fields

        Returns
        -------
        Task
            Updated Task instance with agents loaded

        Raises
        ------
        HTTPException (404 NOT FOUND)
            If task doesn't exist or is soft-deleted
        HTTPException (400 BAD REQUEST)
            If any new agent ID doesn't exist or is soft-deleted

        Examples
        --------
        from app.schemas.task import TaskUpdate

        # Update only status
        update_data = TaskUpdate(status="completed")
        task = await TaskService.update_task(1, update_data)

        # Reassign agents (replaces all existing)
        update_data = TaskUpdate(supported_agent_ids=[2, 4, 5])
        task = await TaskService.update_task(1, update_data)

        # Update multiple fields
        update_data = TaskUpdate(
            title="Enhanced Report Processing",
            status="pending",
            supported_agent_ids=[1, 2]
        )
        task = await TaskService.update_task(1, update_data)

        Notes
        -----
        When updating supported_agent_ids:
        1. All existing agent assignments are removed
        2. New agent assignments are created
        3. This is a complete replacement, not an append
        """
        task = await TaskService.get_task_by_id(task_id)

        # Verify agents if provided
        if task_data.supported_agent_ids is not None:
            if not await AgentService.verify_agents_exist(task_data.supported_agent_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more agent IDs do not exist"
                )

            # Update agents
            await task.agents.clear()
            agents = await Agent.filter(id__in=task_data.supported_agent_ids)
            await task.agents.add(*agents)

        # Update other fields
        update_data = task_data.model_dump(exclude={"supported_agent_ids"}, exclude_unset=True)
        if update_data:
            await task.update_from_dict(update_data).save()

        await task.fetch_related("agents")
        return task

    @staticmethod
    async def delete_task(task_id: int) -> None:
        """
        Soft delete a task by setting deleted_at timestamp.

        The task record remains in the database but is excluded from
        queries. This preserves audit trail and related execution records.

        Parameters
        ----------
        task_id : int
            ID of the task to delete

        Raises
        ------
        HTTPException (404 NOT FOUND)
            If task doesn't exist or is already deleted

        Examples
        --------
        await TaskService.delete_task(1)
        # Task is soft-deleted, not physically removed

        # Subsequent get will raise 404
        try:
            task = await TaskService.get_task_by_id(1)
        except HTTPException:
            print("Task is deleted")

        Notes
        -----
        - TaskAgent junction records are preserved
        - Related Execution records are preserved
        - Agent records are not affected
        - Task can potentially be recovered by clearing deleted_at
        """
        task = await TaskService.get_task_by_id(task_id)
        task.deleted_at = datetime.utcnow()
        await task.save()
