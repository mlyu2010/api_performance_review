"""
Execution Model Module
=====================

This module defines the Execution model for tracking task execution by agents.

The Execution model represents a single execution instance of a task by a specific
agent. It tracks the execution status, timing, results, and any errors that occurred.

Database Table
-------------
Table name: executions

Fields:
- id: Primary key (auto-increment integer)
- task_id: Foreign key to tasks table (CASCADE delete)
- agent_id: Foreign key to agents table (CASCADE delete)
- status: Execution status (running, completed, failed)
- started_at: Timestamp when execution started
- completed_at: Timestamp when execution finished (nullable)
- result: Execution result data (nullable text)
- error_message: Error details if execution failed (nullable text)
- created_at: Timestamp (auto-populated on creation)
- updated_at: Timestamp (auto-updated on modification)

Status Values
------------
Executions can have the following status values:
- 'running': Execution is currently in progress
- 'completed': Execution finished successfully
- 'failed': Execution failed with an error

Relationships
------------
Execution belongs to:
- Task (many-to-one): The task being executed
- Agent (many-to-one): The agent performing the execution

Access related data:
    # Get task for an execution
    task = await execution.task

    # Get agent for an execution
    agent = await execution.agent

    # Get all executions for a task
    executions = await task.executions.all()

    # Get all executions by an agent
    executions = await agent.executions.all()

Usage Examples
-------------
Create an execution:
    execution = await Execution.create(
        task_id=1,
        agent_id=2,
        status="running"
    )

Complete an execution successfully:
    from datetime import datetime
    execution.status = "completed"
    execution.completed_at = datetime.utcnow()
    execution.result = "Task completed successfully"
    await execution.save()

Mark execution as failed:
    execution.status = "failed"
    execution.completed_at = datetime.utcnow()
    execution.error_message = "Connection timeout"
    await execution.save()

Query running executions:
    running = await Execution.filter(status="running").all()

Get execution with related task and agent:
    execution = await Execution.get(id=1).prefetch_related("task", "agent")
"""

from tortoise import fields
from tortoise.models import Model


class Execution(Model):
    """
    Execution model representing a task execution instance by an agent.

    An execution tracks the lifecycle of a task being performed by an agent,
    including when it started, when it completed (if applicable), the result
    or error message, and the current status.

    Each execution is linked to exactly one task and one agent. Multiple
    executions can exist for the same task-agent pair, representing different
    execution attempts over time.

    Attributes
    ----------
    id : int
        Primary key, auto-incremented
    task : ForeignKeyRelation[Task]
        The task being executed
        Cascade delete: If task is deleted, execution records are deleted
    agent : ForeignKeyRelation[Agent]
        The agent performing the execution
        Cascade delete: If agent is deleted, execution records are deleted
    status : str
        Current execution status, max 50 characters
        Valid values: 'running', 'completed', 'failed'
        Default: 'running'
    started_at : datetime
        Timestamp when execution started, auto-populated on creation
    completed_at : datetime, optional
        Timestamp when execution finished, None if still running
    result : str, optional
        Execution result data or output, None if not completed or failed
        Text field with no length limit
    error_message : str, optional
        Error details if execution failed, None if successful or running
        Text field with no length limit
    created_at : datetime
        Timestamp when the execution record was created, auto-populated
    updated_at : datetime
        Timestamp when the execution record was last modified, auto-updated

    Relationships
    ------------
    task : ForeignKeyRelation[Task]
        The task being executed (accessible via execution.task)
    agent : ForeignKeyRelation[Agent]
        The agent executing the task (accessible via execution.agent)

    Methods
    -------
    __str__()
        String representation showing execution details

    Examples
    --------
    Create and track an execution:
        # Start execution
        execution = await Execution.create(
            task_id=1,
            agent_id=2,
            status="running"
        )

        # Complete successfully
        from datetime import datetime
        execution.status = "completed"
        execution.completed_at = datetime.utcnow()
        execution.result = "Processed 1000 records successfully"
        await execution.save()

    Handle execution failure:
        execution.status = "failed"
        execution.completed_at = datetime.utcnow()
        execution.error_message = "Database connection failed: timeout after 30s"
        await execution.save()

    Query execution history:
        # All executions for a task
        executions = await Execution.filter(task_id=1).order_by("-started_at").all()

        # Running executions only
        running = await Execution.filter(status="running").all()

        # Failed executions in last 24 hours
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        failed = await Execution.filter(
            status="failed",
            started_at__gte=yesterday
        ).all()
    """
    id = fields.IntField(pk=True)
    task = fields.ForeignKeyField("models.Task", related_name="executions", on_delete=fields.CASCADE)
    agent = fields.ForeignKeyField("models.Agent", related_name="executions", on_delete=fields.CASCADE)
    status = fields.CharField(max_length=50, default="running")  # running, completed, failed
    started_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)
    result = fields.TextField(null=True)
    error_message = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "executions"

    def __str__(self):
        """
        Return a string representation of the Execution.

        Returns
        -------
        str
            String showing execution ID, task ID, agent ID, and status
            Format: "Execution(id={id}, task_id={task_id}, agent_id={agent_id}, status={status})"

        Examples
        --------
        >>> execution = Execution(id=1, task_id=5, agent_id=3, status="running")
        >>> str(execution)
        'Execution(id=1, task_id=5, agent_id=3, status=running)'
        """
        return f"Execution(id={self.id}, task_id={self.task_id}, agent_id={self.agent_id}, status={self.status})"
