"""
Execution Service Module
=======================

This module provides the ExecutionService class for managing task executions by agents.
It handles creation, retrieval, and simulation of task executions in the system.

The service ensures:
- Task and agent existence verification
- Authorization validation for agents running tasks
- Asynchronous execution simulation
- Status tracking and result management
"""

from datetime import datetime
from typing import List
from fastapi import HTTPException, status
import asyncio

from app.models.execution import Execution
from app.models.task import Task
from app.models.agent import Agent
from app.schemas.execution import ExecutionCreate


class ExecutionService:
    @staticmethod
    async def create_execution(execution_data: ExecutionCreate) -> Execution:
        """
        Create and start a new task execution with a specific agent.

        Parameters
        ----------
        execution_data : ExecutionCreate
            Data transfer object containing task_id and agent_id

        Returns
        -------
        Execution
            The created execution instance

        Raises
        ------
        HTTPException
            404 if task or agent not found
            400 if agent is not authorized for the task
        """
        # Verify task exists
        task = await Task.filter(id=execution_data.task_id, deleted_at__isnull=True).prefetch_related("agents").first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {execution_data.task_id} not found"
            )

        # Verify agent exists
        agent = await Agent.filter(id=execution_data.agent_id, deleted_at__isnull=True).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with id {execution_data.agent_id} not found"
            )

        # Verify agent can run this task
        agent_ids = [a.id for a in await task.agents.all()]
        if execution_data.agent_id not in agent_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent {execution_data.agent_id} is not authorized to run task {execution_data.task_id}"
            )

        # Create execution
        execution = await Execution.create(
            task_id=execution_data.task_id,
            agent_id=execution_data.agent_id,
            status="running"
        )

        # Simulate task execution (in real scenario, this would be async background task)
        asyncio.create_task(ExecutionService._simulate_execution(execution.id))

        return execution

    @staticmethod
    async def get_all_executions() -> List[Execution]:
        """
        Retrieve all executions from the database.

        Returns
        -------
        List[Execution]
            List of all executions with their related task and agent data
        """
        return await Execution.all().prefetch_related("task", "agent")

    @staticmethod
    async def get_running_executions() -> List[Execution]:
        """
        Retrieve all currently running executions.

        Returns
        -------
        List[Execution]
            List of executions with status 'running' and their related task and agent data
        """
        return await Execution.filter(status="running").prefetch_related("task", "agent").all()

    @staticmethod
    async def get_execution_by_id(execution_id: int) -> Execution:
        """
        Retrieve a specific execution by its ID.

        Parameters
        ----------
        execution_id : int
            The ID of the execution to retrieve

        Returns
        -------
        Execution
            The execution instance with its related task and agent data

        Raises
        ------
        HTTPException
            404 if execution with given ID is not found
        """
        execution = await Execution.filter(id=execution_id).prefetch_related("task", "agent").first()
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution with id {execution_id} not found"
            )
        return execution

    @staticmethod
    async def _simulate_execution(execution_id: int):
        """
        Simulate an asynchronous task execution.

        This is a placeholder method that simulates work by waiting for 5 seconds
        and then marks the execution as completed. In a production environment,
        this should be replaced with actual task execution logic.

        Parameters
        ----------
        execution_id : int
            The ID of the execution to simulate
        """
        await asyncio.sleep(5)  # Simulate work

        execution = await Execution.get(id=execution_id)
        execution.status = "completed"
        execution.completed_at = datetime.utcnow()
        execution.result = f"Task {execution.task_id} completed successfully by agent {execution.agent_id}"
        await execution.save()
